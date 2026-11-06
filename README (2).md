# 💧 Reservorio comunitario en tiempos de sequía — La Paz, Bolivia

**Desafío individual · Métodos Numéricos**
EDO de primer orden con condición inicial · Heun · Runge-Kutta 4 · Solución analítica

- **Autora:** Tu nombre completo
- **Materia:** Métodos Numéricos
- **Aplicación web:** _pega aquí el enlace público_
- **Video (1 min):** _pega aquí el enlace_

> Los parámetros del modelo son **hipotéticos**. Los resultados son simulaciones del modelo,
> no predicciones comprobadas con datos reales.

## Problema
El fenómeno de El Niño puede reducir las lluvias y el aporte de agua a un reservorio comunitario
de un barrio (hipotético) de la ciudad de La Paz. Cuando el volumen baja, aparecen racionamientos
y tensiones entre vecinos.

**Pregunta:** ¿en cuántos días el volumen baja del umbral mínimo (300 m³) y qué aporte diario
haría falta para evitarlo?

## Modelo matemático
```
dV/dt = a − k·V ,   V(0) = V₀
```

| Símbolo | Significado | Unidad |
|---|---|---|
| V(t) | Volumen de agua en el reservorio | m³ |
| t | Tiempo | días |
| a | Aporte durante la sequía | m³/día |
| k | Tasa de salida por consumo y pérdidas | 1/día |
| V₀ | Volumen inicial | m³ |

**Supuestos:** aporte constante, salida proporcional al volumen almacenado, sin lluvias extra.

**Parámetros base (hipotéticos):** V₀ = 500 m³, a = 10 m³/día, k = 0,04 día⁻¹, T = 60 días,
umbral = 300 m³.

## Solución analítica
```
V(t) = a/k + (V₀ − a/k)·e^(−k t)          →   V(t) = 250 + 250·e^(−0,04 t)
t* = (1/k)·ln[(V₀ − a/k)/(V_c − a/k)]     →   t* ≈ 40,2 días
a_min = k·V_c                              →   a_min = 12 m³/día
```
Verificación por sustitución: ver la pestaña «Solución analítica» de la app.

## Métodos numéricos
- **Heun (RK2):** `V* = Vₙ + h·f(Vₙ)`; `Vₙ₊₁ = Vₙ + (h/2)[f(Vₙ) + f(V*)]`
- **RK4:** `Vₙ₊₁ = Vₙ + (h/6)(k₁ + 2k₂ + 2k₃ + k₄)`

Ambos usan los mismos parámetros, condición inicial, intervalo y paso h. La app compara dos
tamaños de paso (h₁ y h₂), muestra la tabla por pasos, la gráfica y los errores absoluto y
relativo porcentual.

## Estructura del proyecto
```
app.py            Interfaz web (Streamlit)
modelo.py         EDO, solución analítica, Heun, RK4, errores
db.py             Base de datos SQLite para guardar informes
requirements.txt  Dependencias
informes.db       Se crea automáticamente al ejecutar la app
```

## Ejecución local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Base de datos (SQLite)
Los informes se guardan en `informes.db` (tabla `informes`) con parámetros, errores máximos,
interpretación y la tabla de resultados. En hostings gratuitos (por ejemplo Streamlit Community
Cloud) el archivo puede reiniciarse cuando la app se reinicia; por eso la app también permite
descargar el informe (.md) y la tabla (.csv).

## Despliegue (Streamlit Community Cloud)
1. Sube esta carpeta a un repositorio público de GitHub.
2. Entra a https://share.streamlit.io, inicia sesión con GitHub y elige «New app».
3. Selecciona el repositorio, la rama y el archivo principal `app.py`, y pulsa «Deploy».
4. Copia la URL pública y pégala en este README.

## Limitaciones
Modelo simplificado: el aporte real no es constante, el consumo no siempre es proporcional al
volumen y los parámetros son hipotéticos. Para mayor realismo se podrían contrastar con datos
oficiales (por ejemplo EPSAS o SENAMHI).
