# Guión de presentación — Momento 3
## Intensidad y daño civil en conflictos bélicos recientes (UCDP)

---

## Estructura (15 minutos)

### Slide 1 — El gancho (1 min)
"En 2024, el mundo registró más de X eventos de violencia organizada.
Pero contar eventos no alcanza para entender una guerra.
Hoy les mostramos por qué."

### Slide 2 — Los datos (1.5 min)
- Fuente: Uppsala Conflict Data Program (UCDP)
- 416.000 eventos globales 1989–2024 + datos candidatos 2025–2026
- Subconjunto analizado: 106.000+ eventos desde 2022
- Variables clave: fecha, país, tipo de violencia, muertes estimadas (low/best/high), muertes civiles

### Slide 3 — Hallazgo 1: concentración (2 min)
- 4 conflictos concentran el X% de las muertes: Rusia-Ucrania, Gaza, Etiopía, Sudán
- Gráfico: top países por letalidad (barras horizontales con color = % civil)
- Insight: "No todos los conflictos matan igual"

### Slide 4 — Hallazgo 2: dinámica temporal (2 min)
- Gráfico: trayectorias mensuales por conflicto
- Gaza: pico brutal en oct-nov 2023, sostenido en 2024
- Ucrania: violencia continua sin picos extremos
- Etiopía: escalamiento y descenso
- Insight: "La intensidad tiene formas distintas según el conflicto"

### Slide 5 — Hallazgo 3: daño civil (2 min)
- Gráfico: proporción de muertes civiles por conflicto
- Gaza vs Ucrania: diferencia en el tipo de violencia
- Insight: "El tipo de actor y estrategia define quién muere"

### Slide 6 — La capa de ML (3 min)
**Pregunta del modelo:** ¿Puede la frecuencia mensual de eventos predecir las muertes?

- Modelo: Decision Tree Regressor (max_depth=5)
- Variables de entrada: eventos/mes, muertes civiles
- Variable objetivo: fatalities_best (muertes totales/mes)

**Resultados:**
- R² = [completar con tu valor]
- RMSE = [completar] muertes/mes de error promedio
- Sin overfitting significativo (gap < 0.10)

**Conclusión del modelo:**
"El árbol de decisión — al igual que la regresión lineal simple — tiene un R² bajo.
Eso no es una falla técnica. Es el hallazgo más importante:
la frecuencia de eventos NO explica la letalidad.
Lo que importa es la intensidad por evento, quiénes son los actores y cuántos civiles involucra."

### Slide 7 — Cierre (1.5 min)
**Conclusión principal:**
Contar eventos no basta para entender una guerra.
La frecuencia mensual ayuda, pero la intensidad por evento,
el daño civil y la incertidumbre de las estimaciones cambian la historia.

**Limitaciones:**
- UCDP registra solo eventos letales reportados
- Datos Candidate son preliminares y pueden cambiar
- Regresión lineal y árbol de decisión no capturan causalidad

**Próximos pasos:**
- Incluir tipo de violencia como variable en el modelo
- Entrenar por conflicto en vez de globalmente
- Usar Random Forest para reducir overfitting

---

## Tips para la defensa oral

- No abrir con código — abrir con la pregunta
- Cuando muestres el R² bajo: "Esto es el hallazgo, no el error"
- Si preguntan por el overfitting: "Con ~40 meses de datos el riesgo es real, por eso usamos max_depth=5"
- Si preguntan por los datos Candidate: "Son preliminares, los tratamos con cautela en el análisis"
