# Proyecto: intensidad y daño civil en conflictos bélicos recientes

Este proyecto analiza eventos de violencia organizada registrados por UCDP para contar una historia clara: **en los conflictos recientes, la cantidad de eventos violentos no siempre explica por si sola la letalidad; algunos conflictos concentran muchas muertes en pocos episodios y otros muestran una violencia mas frecuente pero menos letal por evento**.

## Objetivo

Responder, con limpieza de datos, EDA, visualizacion y regresion lineal:

> ¿Como ha cambiado la intensidad de los conflictos armados recientes desde 2022, que paises concentran la mayor letalidad y que tanto predice la frecuencia mensual de eventos el numero de muertes estimadas?

## Datos

Fuente principal: Uppsala Conflict Data Program (UCDP).

- `GED 25.1`: eventos globales de violencia organizada entre 1989 y 2024.
- `Candidate GED 2025`: eventos candidatos acumulados de enero a diciembre de 2025.
- `Candidate GED 26.0.3`: eventos candidatos publicados hasta marzo de 2026.

Tamano verificado en este proyecto:

- Base cruda integrada: **416.101 filas**.
- Subconjunto reciente procesado desde 2022: **106.259 filas**.
- Variables clave: fecha, pais, conflicto, tipo de violencia, coordenadas, precision temporal/geografica, muertes estimadas bajas/altas/mejores y muertes civiles.

## Por que esta base sirve para el trabajo

- Es grande, publica y academica.
- No llega lista para presentar: exige limpiar fechas, codigos de precision, valores centinela como `-1`, textos, tipos numericos, rangos de fatalidades, coordenadas y columnas de incertidumbre.
- Permite reutilizar lo visto en clase: inspeccion inicial, limpieza, filtros, `groupby`, analisis univariado, analisis bivariado, visualizaciones, storytelling, app interactiva y regresion lineal.

## Estructura

```text
proyecto_conflicto_ucdp/
  app/
    streamlit_app.py
  data/
    raw/
    processed/
  notebooks/
    01_analisis_conflictos_ucdp.ipynb
  reports/
    guion_presentacion.md
  src/
    ucdp_pipeline.py
  requirements.txt
```

## Como ejecutar

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Abrir el notebook:

```bash
jupyter notebook notebooks/01_analisis_conflictos_ucdp.ipynb
```

Ejecutar la app:

```bash
streamlit run app/streamlit_app.py
```

## Entregables

- Notebook explicativo con paso a paso, limpieza, EDA, visualizaciones y regresion.
- Archivos procesados en `data/processed`.
- App interactiva en Streamlit.
- Guion breve para presentar el jueves.

## Recomendaciones de presentacion

- No abrir con codigo: abrir con la pregunta de investigacion.
- Mostrar primero el tamano y origen de la base.
- Explicar tres decisiones de limpieza con ejemplos concretos.
- Usar la regresion como apoyo, no como verdad absoluta.
- Cerrar con limitaciones: UCDP cuenta eventos letales reportados; los datos Candidate son preliminares y pueden cambiar.

## Correccion academica agregada

La version actual incluye una app mas orientada a exposicion academica:

- Pregunta de investigacion e hipotesis.
- Marco metodologico.
- Comparacion de casos clave: Rusia-Ucrania, Etiopia, Israel-Palestina y Sudan.
- Regresion global y regresiones por caso.
- Conclusiones claras para defender oralmente.

Tambien se agregaron documentos de apoyo en `reports/`:

- `metodologia_conclusiones_academicas.md`
- `presentacion_10_min_3_integrantes.md`
- `checklist_entrega.md`
