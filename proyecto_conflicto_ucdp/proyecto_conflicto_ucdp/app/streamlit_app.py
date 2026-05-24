"""
streamlit_app.py
App interactiva para explorar conflictos UCDP.
Ejecutar: streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from ucdp_pipeline import (
    load_raw_events, clean_events,
    build_monthly_panel, build_global_monthly,
    linear_regression_summary,
)

# ------------------------------------------------------------------
st.set_page_config(
    page_title="Conflictos UCDP — Analítica de Datos",
    page_icon="🌍",
    layout="wide",
)

DATA_DIR = PROJECT_ROOT / "data"

# ------------------------------------------------------------------
@st.cache_data
def load_data():
    raw   = load_raw_events(DATA_DIR)
    clean = clean_events(raw)
    panel = build_monthly_panel(clean, min_year=2022)
    gm    = build_global_monthly(panel)
    return clean, panel, gm

# ------------------------------------------------------------------
st.title("Intensidad y daño civil en conflictos recientes")
st.markdown(
    "**Pregunta guía:** ¿Cómo ha cambiado la intensidad de los conflictos armados "
    "desde 2022, qué países concentran la mayor letalidad y qué tanto predice "
    "la frecuencia mensual de eventos el número de muertes estimadas?"
)

try:
    clean, panel, global_monthly = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# ------------------------------------------------------------------
# Sidebar — filtros
# ------------------------------------------------------------------
st.sidebar.header("Filtros")

years = sorted(clean["year"].dropna().unique().astype(int))
year_range = st.sidebar.slider("Rango de años", int(min(years)), int(max(years)),
                                (2022, int(max(years))))

violence_opts = ["Todos"] + sorted(clean["violence_label"].dropna().unique().tolist()) \
    if "violence_label" in clean.columns else ["Todos"]
violence_sel = st.sidebar.selectbox("Tipo de violencia", violence_opts)

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
mask = (clean["year"] >= year_range[0]) & (clean["year"] <= year_range[1])
if violence_sel != "Todos" and "violence_label" in clean.columns:
    mask &= (clean["violence_label"] == violence_sel)
filtered = clean[mask]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Eventos", f"{len(filtered):,}")
col2.metric("Muertes estimadas", f"{filtered['best'].sum():,.0f}")
col3.metric("Muertes civiles",   f"{filtered['deaths_civilians'].sum():,.0f}")
col4.metric("Países",            f"{filtered['country'].nunique()}" if "country" in filtered.columns else "—")

st.divider()

# ------------------------------------------------------------------
# Letalidad mensual global
# ------------------------------------------------------------------
st.subheader("Letalidad mensual global")
fig_line = px.line(
    global_monthly, x="event_month",
    y=["fatalities_best", "civilian_fatalities"],
    labels={"value": "Muertes", "event_month": "Mes", "variable": "Serie"},
    color_discrete_sequence=["#246A73", "#D9A441"],
)
st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------------------------------
# Top países
# ------------------------------------------------------------------
st.subheader("Países con mayor letalidad")
if "country" in filtered.columns:
    top = (
        filtered.groupby("country")
        .agg(eventos=("id","count"), muertes=("best","sum"), civiles=("deaths_civilians","sum"))
        .sort_values("muertes", ascending=False)
        .head(15)
        .reset_index()
    )
    top["prop_civil"] = (top["civiles"] / top["muertes"] * 100).round(1)
    fig_bar = px.bar(
        top, x="muertes", y="country", orientation="h",
        color="prop_civil",
        color_continuous_scale="RdYlGn_r",
        labels={"muertes":"Muertes estimadas","country":"País","prop_civil":"% civil"},
    )
    fig_bar.update_layout(yaxis={"autorange":"reversed"})
    st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------------
# Regresión lineal: eventos vs muertes
# ------------------------------------------------------------------
st.subheader("Regresión: eventos mensuales vs muertes estimadas")
metrics = linear_regression_summary(global_monthly, target="fatalities_best")
x_line = np.array([global_monthly["events"].min(), global_monthly["events"].max()])
y_line = metrics["intercept"] + metrics["slope"] * x_line

fig_reg = px.scatter(
    global_monthly, x="events", y="fatalities_best",
    hover_data=["event_month"],
    labels={"events":"Eventos/mes","fatalities_best":"Muertes/mes"},
)
fig_reg.add_scatter(x=x_line, y=y_line, mode="lines", name="Regresión lineal",
                    line=dict(color="#D9A441", width=2))
st.plotly_chart(fig_reg, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Pendiente",  f"{metrics['slope']:,.1f}")
c2.metric("R²",         f"{metrics['r2']:.3f}")
c3.metric("RMSE",       f"{metrics['rmse']:,.0f}")

st.caption(
    "Un R² bajo confirma la hipótesis del proyecto: la frecuencia de eventos "
    "no explica por sí sola la letalidad. Algunos conflictos concentran muchas "
    "muertes en pocos episodios de alta intensidad."
)
