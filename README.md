# 💧 Reservorio comunitario en tiempos de sequía — La Paz, Bolivia

**Desafío individual · Métodos Numéricos**

EDO de primer orden con condición inicial · Método de Heun · Runge-Kutta 4 · Solución analítica

- **Autora:** Tarqui Humerez Mayra Belen
- **Materia:** Métodos Numéricos
- **Aplicación web:** https://desafio-ecuaciones-diferenciales-a9jrw6aht6t4r2dze7pukp.streamlit.app/
- **Video (1 min):** https://youtu.be/lDhrBNXsnkk
  
> **Nota:** Los parámetros del modelo son hipotéticos. Los resultados representan simulaciones matemáticas y no predicciones comprobadas con datos reales.

## 1. Problema

El fenómeno de El Niño puede reducir las lluvias y el aporte de agua a un reservorio comunitario de un barrio hipotético de la ciudad de La Paz. Cuando el volumen almacenado disminuye, pueden presentarse racionamientos y tensiones entre los vecinos.

**Pregunta principal:** ¿En cuántos días el volumen de agua alcanza el umbral mínimo de 300 m³ y qué aporte diario sería necesario para evitar que el reservorio descienda por debajo de ese nivel?

## 2. Modelo matemático

Se plantea una ecuación diferencial ordinaria de primer orden:

```text
dV/dt = a − k·V,   V(0) = V₀
```

| Símbolo | Significado | Unidad |
|---|---|---|
| V(t) | Volumen de agua en el reservorio | m³ |
| t | Tiempo | días |
| a | Aporte diario de agua durante la sequía | m³/día |
| k | Tasa de salida por consumo y pérdidas | 1/día |
| V₀ | Volumen inicial del reservorio | m³ |

**Supuestos del modelo:**
- El aporte de agua permanece constante durante la simulación.
- La salida de agua es proporcional al volumen almacenado.
- No se consideran lluvias adicionales ni otros aportes extraordinarios.

**Parámetros base (hipotéticos):**

- Volumen inicial: V₀ = 500 m³
- Aporte diario: a = 10 m³/día
- Tasa de salida: k = 0,04 día⁻¹
- Tiempo de simulación: T = 60 días
- Umbral mínimo: Vc = 300 m³

## 3. Solución analítica

La solución exacta de la ecuación diferencial es:

```text
V(t) = a/k + (V₀ − a/k)·e^(−kt)
```

Sustituyendo los parámetros iniciales:

```text
V(t) = 250 + 250·e^(−0,04t)
```

El tiempo en que el volumen alcanza el umbral mínimo se obtiene mediante:

```text
t* = (1/k)·ln[(V₀ − a/k)/(Vc − a/k)]

t* ≈ 40,2 días
```

El aporte mínimo necesario para mantener el volumen de equilibrio en el umbral se calcula mediante:

```text
a_min = k·Vc

a_min = 12 m³/día
```

La aplicación permite verificar estos resultados mediante sustitución en la pestaña **«Solución analítica»**.

## 4. Métodos numéricos

Para aproximar la solución de la ecuación diferencial se implementaron dos métodos numéricos:

**Método de Heun (RK2)**

```text
V* = Vₙ + h·f(Vₙ)

Vₙ₊₁ = Vₙ + (h/2)·[f(Vₙ) + f(V*)]
```

**Método de Runge-Kutta de cuarto orden (RK4)**

```text
Vₙ₊₁ = Vₙ + (h/6)·(k₁ + 2k₂ + 2k₃ + k₄)
```

Ambos métodos utilizan los mismos parámetros, condición inicial e intervalo de simulación. La aplicación permite comparar dos tamaños de paso (h₁ y h₂), visualizar los resultados mediante tablas y gráficas, y analizar los errores absolutos y relativos porcentuales.

## 5. Funcionalidades de la aplicación

La aplicación web desarrollada con Streamlit incluye:

- **Simulación:** permite modificar los parámetros y observar la evolución del volumen del reservorio.
- **Comparación de pasos:** analiza los resultados de Heun y RK4 utilizando diferentes tamaños de paso.
- **Solución analítica:** presenta el desarrollo matemático, la sustitución de parámetros y el resultado teórico.
- **Diagnóstico del reservorio:** identifica situaciones críticas, favorables y límite según el volumen de equilibrio y el umbral mínimo.
- **Gráficas:** representan la evolución del volumen, el umbral mínimo, el volumen de equilibrio y los errores de los métodos.
- **Historial de informes:** permite guardar, consultar y revisar simulaciones anteriores.
- **Exportación de resultados:** permite descargar informes en formato PDF y Excel.

## 6. Estructura del proyecto

```text
app.py            Interfaz web desarrollada con Streamlit
modelo.py         EDO, solución analítica, Heun, RK4 y errores
db.py             Gestión de la base de datos SQLite
requirements.txt  Dependencias del proyecto
informes.db       Base de datos creada automáticamente
```

## 7. Ejecución local

Para ejecutar el proyecto en un entorno local:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 8. Base de datos

Se utiliza SQLite para almacenar los informes de simulación en el archivo `informes.db`, dentro de la tabla `informes`.

Los registros incluyen los parámetros utilizados, errores máximos, interpretación y resultados de la simulación.

**Consideración:** en servicios de alojamiento gratuitos, como Streamlit Community Cloud, el almacenamiento local puede ser temporal y perderse cuando se reinicia o se vuelve a desplegar la aplicación. Por ello, se permite descargar los informes en PDF y Excel.

## 9. Despliegue

La aplicación se encuentra publicada mediante **Streamlit Community Cloud** y vinculada a un repositorio de GitHub.

Enlace de acceso:

https://desafio-ecuaciones-diferenciales-a9jrw6aht6t4r2dze7pukp.streamlit.app/

## 10. Limitaciones del modelo

El modelo representa una situación simplificada. En la realidad, el aporte de agua no permanece necesariamente constante, el consumo puede variar y las pérdidas no siempre son proporcionales al volumen almacenado.

Además, los parámetros utilizados son hipotéticos. Para obtener una representación más realista sería necesario contrastarlos con información oficial de instituciones como EPSAS o SENAMHI.

Como trabajo futuro, se podría incorporar información real sobre precipitaciones, consumo de agua y variaciones estacionales para mejorar la precisión de las simulaciones.
