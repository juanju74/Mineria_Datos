"""
ucdp_pipeline.py
Pipeline de carga, limpieza y agregación para datos UCDP.
Semanas 2-14 del proyecto de Analítica de Datos.
"""
from __future__ import annotations

from pathlib import Path
import io
import urllib.request
import zipfile

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Rutas esperadas de los archivos raw
# ---------------------------------------------------------------------------
RAW_FILES = {
    "ged251":        "GED251.csv",
    "candidate2025": "CandidateGED2025.csv",
    "candidate2026": "CandidateGED2026.csv",
}

DOWNLOAD_URLS = {
    "ged251":        "https://ucdp.uu.se/downloads/ged/ged251-csv.zip",
    "candidate2026": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_3.csv",
}

CANDIDATE_GROUP = {"candidate2025", "candidate2026"}


def _download_ged251(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DOWNLOAD_URLS["ged251"], timeout=120) as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as zf:
            csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise RuntimeError("No se encontró el CSV dentro del archivo ZIP de GED251.")
            with zf.open(csv_names[0]) as zf_obj:
                path.write_bytes(zf_obj.read())


def _download_candidate_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DOWNLOAD_URLS["candidate2026"], timeout=120) as response:
        path.write_bytes(response.read())


def ensure_data_files(data_dir: Path, download: bool = False) -> list[Path]:
    """Verifica qué archivos raw faltan. Retorna lista de paths faltantes."""
    raw_dir = data_dir / "raw"
    candidate_present = any((raw_dir / RAW_FILES[key]).exists() for key in CANDIDATE_GROUP)
    missing = []
    for key, fname in RAW_FILES.items():
        path = raw_dir / fname
        if key in CANDIDATE_GROUP:
            continue
        if not path.exists():
            missing.append(path)
    if not candidate_present:
        missing.append(raw_dir / RAW_FILES["candidate2026"])

    if missing and download:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for path in missing:
            if path.name == RAW_FILES["ged251"]:
                print(f"Descargando GED251 a {path}...")
                _download_ged251(path)
            elif path.name == RAW_FILES["candidate2026"]:
                print(f"Descargando CandidateGED2026 a {path}...")
                _download_candidate_csv(path)
            else:
                print(f"No hay una descarga automática configurada para {path.name}.")
        # Recompute missing after attempted downloads
        missing = [path for path in missing if not path.exists()]
    return missing


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def load_raw_events(data_dir: Path) -> pd.DataFrame:
    """Carga y concatena los tres archivos UCDP en un único DataFrame."""
    frames = []
    for key, fname in RAW_FILES.items():
        path = data_dir / "raw" / fname
        if path.exists():
            df = pd.read_csv(path, low_memory=False)
            df["_source_file"] = key
            frames.append(df)
    if not frames:
        raise FileNotFoundError(
            f"No se encontró ningún archivo raw en {data_dir / 'raw'}.\n"
            "Descarga los archivos desde https://ucdp.uu.se/downloads/ y ponlos en data/raw/"
        )
    raw = pd.concat(frames, ignore_index=True)
    return raw


# ---------------------------------------------------------------------------
# Diagnóstico inicial
# ---------------------------------------------------------------------------
def initial_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Reporte de calidad: nulos, tipos y valores únicos por columna."""
    report = pd.DataFrame({
        "tipo":       df.dtypes,
        "nulos":      df.isnull().sum(),
        "pct_nulo":   (df.isnull().mean() * 100).round(1),
        "unicos":     df.nunique(),
        "ejemplo":    df.iloc[0] if len(df) > 0 else None,
    })
    return report


# ---------------------------------------------------------------------------
# Limpieza
# ---------------------------------------------------------------------------
def clean_events(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza principal del dataset UCDP:
    - Convierte fechas a datetime
    - Convierte numéricas con pd.to_numeric
    - Elimina duplicados por id
    - Trata number_of_sources=-1 como nulo
    - Crea variables derivadas: year, month, event_month, uncertainty, civil_ratio
    """
    df = raw.copy()
    duplicates_before = df.duplicated("id").sum()

    # Fechas
    for col in ["date_start", "date_end"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Numéricas
    num_cols = ["best", "high", "low", "deaths_civilians",
                "number_of_sources", "latitude", "longitude"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Duplicados
    df = df.drop_duplicates(subset="id", keep="first")
    duplicates_removed = duplicates_before - df.duplicated("id").sum()

    # Valor centinela -1 en number_of_sources
    if "number_of_sources" in df.columns:
        df.loc[df["number_of_sources"] == -1, "number_of_sources"] = np.nan

    # Variables derivadas
    if "date_start" in df.columns:
        df["year"]        = df["date_start"].dt.year
        df["month"]       = df["date_start"].dt.month
        df["event_month"] = df["date_start"].dt.to_period("M").dt.to_timestamp()

    if "high" in df.columns and "low" in df.columns:
        df["uncertainty"] = df["high"] - df["low"]

    if "deaths_civilians" in df.columns and "best" in df.columns:
        df["civil_ratio"] = df["deaths_civilians"] / df["best"].replace(0, np.nan)

    # Etiquetas legibles para type_of_violence
    violence_map = {1: "State-based", 2: "Non-state", 3: "One-sided"}
    if "type_of_violence" in df.columns:
        df["violence_label"] = df["type_of_violence"].map(violence_map)

    df.attrs["duplicates_removed"] = int(duplicates_removed)
    return df


# ---------------------------------------------------------------------------
# Paneles agregados
# ---------------------------------------------------------------------------
def build_monthly_panel(clean: pd.DataFrame, min_year: int = 2022) -> pd.DataFrame:
    """
    Panel mensual por conflicto:
    Una fila = un mes + conflict_name.
    Columnas: events, fatalities_best, civilian_fatalities, uncertainty_total.
    """
    recent = clean[clean["year"] >= min_year].copy()

    agg_cols = {
        "events":               ("id", "count"),
        "fatalities_best":      ("best", "sum"),
        "civilian_fatalities":  ("deaths_civilians", "sum"),
    }
    if "uncertainty" in recent.columns:
        agg_cols["uncertainty_total"] = ("uncertainty", "sum")
    if "high" in recent.columns:
        agg_cols["high_fatalities"] = ("high", "sum")
    if "low" in recent.columns:
        agg_cols["low_fatalities"] = ("low", "sum")

    group_cols = ["event_month"]
    if "conflict_name" in recent.columns:
        group_cols.append("conflict_name")
    if "country" in recent.columns:
        group_cols.append("country")
    if "type_of_violence" in recent.columns:
        group_cols.append("type_of_violence")

    panel = (
        recent
        .groupby(group_cols, as_index=False)
        .agg(**agg_cols)
        .sort_values("event_month")
    )
    return panel


def build_global_monthly(monthly_panel: pd.DataFrame) -> pd.DataFrame:
    """Panel mensual global (suma de todos los conflictos por mes)."""
    num_cols = [c for c in monthly_panel.columns
                if c not in ["event_month", "conflict_name", "country", "type_of_violence"]]
    global_m = (
        monthly_panel
        .groupby("event_month", as_index=False)[num_cols]
        .sum()
        .sort_values("event_month")
    )
    return global_m


# ---------------------------------------------------------------------------
# Regresión lineal simple (semanas anteriores)
# ---------------------------------------------------------------------------
def linear_regression_summary(df: pd.DataFrame, target: str = "fatalities_best") -> dict:
    """
    Regresión lineal simple: events → target.
    Retorna dict con slope, intercept, r2, rmse, months.
    """
    from scipy import stats

    sub = df[["events", target]].dropna()
    if len(sub) < 3:
        return {"slope": np.nan, "intercept": np.nan, "r2": np.nan,
                "rmse": np.nan, "months": len(sub)}

    slope, intercept, r, p, se = stats.linregress(sub["events"], sub[target])
    y_pred = intercept + slope * sub["events"]
    rmse = np.sqrt(((sub[target] - y_pred) ** 2).mean())
    return {
        "slope":     round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r2":        round(float(r ** 2), 4),
        "rmse":      round(float(rmse), 2),
        "months":    len(sub),
    }


# ---------------------------------------------------------------------------
# Exportar procesados
# ---------------------------------------------------------------------------
def export_processed(data_dir: Path, clean: pd.DataFrame, min_year: int = 2022) -> dict:
    """Guarda archivos procesados en data/processed/."""
    out_dir = data_dir / "processed"
    out_dir.mkdir(exist_ok=True)

    recent = clean[clean["year"] >= min_year]
    panel  = build_monthly_panel(clean, min_year=min_year)
    global_m = build_global_monthly(panel)

    paths = {
        "events_recent":  out_dir / "events_recent.csv",
        "monthly_panel":  out_dir / "monthly_panel.csv",
        "global_monthly": out_dir / "global_monthly.csv",
    }
    recent.to_csv(paths["events_recent"],  index=False)
    panel.to_csv(paths["monthly_panel"],   index=False)
    global_m.to_csv(paths["global_monthly"], index=False)

    return {k: str(v) for k, v in paths.items()}
