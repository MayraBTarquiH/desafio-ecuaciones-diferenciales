"""
Reservorio comunitario en tiempos de sequía (El Niño) — La Paz, Bolivia
Desafío individual · Métodos Numéricos · EDO de primer orden con condición inicial

Ejecutar:  streamlit run app.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import db
import modelo as m

# ---------------------------------------------------------------------------
# Datos de la entrega (EDITA ESTAS LÍNEAS)
# ---------------------------------------------------------------------------
AUTOR = "Tarqui Humerez Mayra Belen"
MATERIA = "Métodos Numéricos"
TITULO_DESAFIO = "Reservorio comunitario en tiempos de sequía: ¿cuánto tiempo nos alcanza el agua?"

st.set_page_config(
    page_title="Reservorio en sequía · La Paz",
    page_icon="💧",
    layout="wide",
)
db.init_db()

# ---------------------------------------------------------------------------
# Estilo: paleta de azules y celestes pastel (tema agua)
# ---------------------------------------------------------------------------
C_FONDO = "#F3FAFE"
C_PANEL = "#FFFFFF"
C_TEXTO = "#1F3A4D"
C_EXACTA = "#1F4E79"   # azul marino suave
C_HEUN = "#6BB3E0"     # celeste
C_RK4 = "#3FA7A0"      # turquesa
C_UMBRAL = "#E59A9A"   # coral pastel
C_EQUILIBRIO = "#8FA8B8"

st.markdown(
    """
    <style>
    h1, h2, h3 { color: #1F4E79; }
    [data-testid="stSidebar"] { background-color: #DDEFFA; }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #BFDDF1;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 2px 6px rgba(74, 144, 194, 0.12);
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #BFDDF1;
        border-radius: 12px;
    }
    .stButton > button, .stDownloadButton > button {
        background-color: #6BB3E0;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #4A90C2;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Encabezado y explicación del problema
# ---------------------------------------------------------------------------
st.title("💧 " + TITULO_DESAFIO)
st.caption(f"{AUTOR} · {MATERIA} · Parámetros HIPOTÉTICOS (no son datos reales)")

with st.expander("¿Qué problema estudia esta simulación?", expanded=True):
    st.markdown(
        """
**Comunidad:** un barrio hipotético de la ciudad de La Paz (Bolivia) abastecido por un
reservorio comunitario.

**Problema:** el fenómeno de El Niño puede reducir las lluvias y, con ello, el aporte de agua
al reservorio. Cuando el volumen baja, aparecen racionamientos y tensiones entre vecinos.

**Pregunta del desafío:** ¿en cuántos días el volumen baja del nivel mínimo (umbral) para
repartir el agua con normalidad, y qué aporte diario haría falta para evitarlo?

**Modelo (EDO de primer orden con condición inicial):**
`dV/dt = a − k·V`, con `V(0) = V₀`

| Símbolo | Significado | Unidad |
|---|---|---|
| V(t) | Volumen de agua en el reservorio | m³ |
| t | Tiempo | días |
| a | Aporte de agua durante la sequía | m³/día |
| k | Tasa de salida por consumo y pérdidas | 1/día |
| V₀ | Volumen inicial | m³ |

**Supuestos:** aporte constante, salida proporcional al volumen almacenado y sin lluvias
extra durante el periodo simulado. Es un modelo simplificado y no una predicción comprobada.
"""
    )

# ---------------------------------------------------------------------------
# Entradas (barra lateral) con validación básica
# ---------------------------------------------------------------------------
st.sidebar.header("Parámetros de la simulación")
V0 = st.sidebar.number_input(
    "Volumen inicial V₀ (m³)", min_value=0.0, value=500.0, step=10.0, format="%.2f"
)
a = st.sidebar.number_input(
    "Aporte durante la sequía a (m³/día)", min_value=0.0, value=10.0, step=0.5, format="%.2f"
)
k = st.sidebar.number_input(
    "Tasa de salida k (1/día)", min_value=0.0001, value=0.04, step=0.005, format="%.4f"
)
Vc = st.sidebar.number_input(
    "Umbral de volumen mínimo (m³)", min_value=0.0, value=300.0, step=10.0, format="%.2f"
)
T = st.sidebar.number_input(
    "Tiempo de simulación (días)", min_value=1.0, value=60.0, step=1.0, format="%.1f"
)
h = st.sidebar.number_input(
    "Tamaño de paso h₁ (días)", min_value=0.01, value=10.0, step=0.5, format="%.2f"
)
h2 = st.sidebar.number_input(
    "Segundo tamaño de paso h₂ (días)", min_value=0.01, value=2.0, step=0.5, format="%.2f"
)

errores = []
advertencias = []
if V0 < 0:
    errores.append("V₀ no puede ser negativo.")
if a < 0:
    errores.append("El aporte a no puede ser negativo.")
if k <= 0:
    errores.append("k debe ser mayor que 0.")
if Vc < 0:
    errores.append("El umbral no puede ser negativo.")
if T <= 0:
    errores.append("El tiempo de simulación debe ser mayor que 0.")
if h <= 0 or h2 <= 0:
    errores.append("Los tamaños de paso deben ser mayores que 0.")
if not errores:
    if h > T or h2 > T:
        errores.append("Los tamaños de paso no pueden ser mayores que el tiempo de simulación.")
    elif m.numero_pasos(T, h) > m.MAX_PASOS or m.numero_pasos(T, h2) > m.MAX_PASOS:
        errores.append(f"Demasiados pasos (máximo {m.MAX_PASOS}). Aumenta h o reduce el tiempo.")
    if h == h2:
        advertencias.append("h₁ y h₂ son iguales: usa dos valores distintos para comparar.")
    if k * max(h, h2) >= 2:
        advertencias.append(
            "k·h es grande (≥ 2): los métodos numéricos pueden volverse inestables. "
            "Reduce h."
        )
    if T / h != round(T / h) or T / h2 != round(T / h2):
        advertencias.append(
            "El tiempo de simulación no es múltiplo exacto de h: la última fila "
            "de la tabla llega un poco más allá de T."
        )

if errores:
    for e in errores:
        st.error(e)
    st.stop()
for w in advertencias:
    st.warning(w)

# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
df1 = m.simular(V0, a, k, h, T)
df2 = m.simular(V0, a, k, h2, T)
res1 = m.resumen_errores(df1)
res2 = m.resumen_errores(df2)
t_umbral = m.tiempo_umbral(V0, a, k, Vc)
a_min = m.aporte_minimo(k, Vc)
v_inf = a / k
texto_interp = m.interpretacion(V0, a, k, Vc, T, t_umbral)

COLUMNAS_DECIMALES = {
    c: "{:.4f}" for c in df1.columns if c not in ("Paso",)
}


def _estilo_ejes(fig, ax):
    fig.patch.set_facecolor(C_FONDO)
    ax.set_facecolor(C_PANEL)
    ax.grid(color="#CFE5F3", alpha=0.9)
    for borde in ax.spines.values():
        borde.set_color("#BFDDF1")
    ax.tick_params(colors=C_TEXTO)
    ax.xaxis.label.set_color(C_TEXTO)
    ax.yaxis.label.set_color(C_TEXTO)
    ax.title.set_color(C_EXACTA)


def grafica_curvas(df, titulo):
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        df["t (días)"],
        df["V exacto (m³)"],
        "-",
        color=C_EXACTA,
        lw=2.2,
        label="Solución analítica",
    )

    ax.plot(
        df["t (días)"],
        df["V Heun (m³)"],
        "s--",
        color=C_HEUN,
        ms=5,
        label="Heun",
    )

    ax.plot(
        df["t (días)"],
        df["V RK4 (m³)"],
        "o:",
        color=C_RK4,
        ms=5,
        label="RK4",
    )

    ax.axhline(
        Vc,
        color=C_UMBRAL,
        ls="--",
        lw=1.3,
        label=f"Umbral ({Vc:,.0f} m³)",
    )

    # Marcar el momento en que se alcanza el umbral
    if t_umbral is not None and t_umbral <= df["t (días)"].iloc[-1]:

        ax.axvline(
            t_umbral,
            color=C_UMBRAL,
            ls="-.",
            lw=1.5,
            label="Día de cruce del umbral",
        )

        ax.scatter(
            t_umbral,
            Vc,
            color="#D65F5F",
            s=85,
            zorder=5,
            edgecolors="white",
            linewidths=1.2,
        )

        ax.annotate(
            f"Día {t_umbral:.2f}\n{Vc:,.0f} m³",
            xy=(t_umbral, Vc),
            xytext=(12, 14),
            textcoords="offset points",
            fontsize=8,
            color=C_TEXTO,
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc=C_PANEL,
                ec="#BFDDF1",
            ),
            arrowprops=dict(
                arrowstyle="->",
                color=C_UMBRAL,
            ),
        )

    ax.axhline(
        v_inf,
        color=C_EQUILIBRIO,
        ls=":",
        lw=1.3,
        label=f"Equilibrio a/k ({v_inf:,.1f} m³)",
    )

    ax.set_xlabel("Tiempo (días)")
    ax.set_ylabel("Volumen V (m³)")
    ax.set_title(titulo)

    ax.legend(fontsize=8, facecolor=C_PANEL, edgecolor="#BFDDF1")

    _estilo_ejes(fig, ax)
    fig.tight_layout()

    return fig


def grafica_errores(df, titulo):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(df["t (días)"], df["Error abs. Heun (m³)"], "s--", color=C_HEUN, ms=5, label="Heun")
    ax.plot(df["t (días)"], df["Error abs. RK4 (m³)"], "o:", color=C_RK4, ms=5, label="RK4")
    ax.set_xlabel("Tiempo (días)")
    ax.set_ylabel("Error absoluto (m³)")
    ax.set_title(titulo)
    ax.legend(fontsize=8, facecolor=C_PANEL, edgecolor="#BFDDF1")
    _estilo_ejes(fig, ax)
    fig.tight_layout()
    return fig


def informe_markdown():
    lineas = [
        f"# {TITULO_DESAFIO}",
        f"{AUTOR} · {MATERIA}",
        "",
        "## Modelo",
        "dV/dt = a − k·V, V(0) = V₀  (parámetros hipotéticos)",
        "",
        "## Parámetros",
        f"- V₀ = {V0:,.2f} m³",
        f"- a = {a:,.2f} m³/día",
        f"- k = {k:.4f} 1/día",
        f"- Umbral = {Vc:,.2f} m³",
        f"- Tiempo de simulación = {T:,.1f} días",
        f"- h₁ = {h:g} días, h₂ = {h2:g} días",
        "",
        "## Resultados",
        f"- Volumen de equilibrio a/k = {v_inf:,.2f} m³",
        "- Días hasta el umbral (solución analítica): "
        + ("no se alcanza" if t_umbral is None else f"{t_umbral:,.2f}"),
        f"- Aporte mínimo para sostener el umbral = {a_min:,.2f} m³/día",
        f"- Error absoluto máximo con h₁: Heun = {res1['Heun']['max_abs']:.4f} m³, "
        f"RK4 = {res1['RK4']['max_abs']:.4f} m³",
        f"- Error absoluto máximo con h₂: Heun = {res2['Heun']['max_abs']:.4f} m³, "
        f"RK4 = {res2['RK4']['max_abs']:.4f} m³",
        "",
        "## Interpretación",
        texto_interp,
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Pestañas
# ---------------------------------------------------------------------------
tab_sim, tab_comp, tab_teoria, tab_hist = st.tabs(
    ["📈 Simulación", "⚖️ Comparar pasos", "📐 Solución analítica", "🗂️ Historial de informes"]
)

# ---- Simulación -----------------------------------------------------------
with tab_sim:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Volumen de equilibrio", f"{v_inf:,.1f} m³")

    c2.metric(
        "Días hasta el umbral",
        "No se alcanza" if t_umbral is None else f"{t_umbral:,.1f} días",
    )

    c3.metric(
        "Aporte mínimo para el equilibrio en el umbral",
        f"{a_min:,.2f} m³/día",
    )

    c4.metric(
        "Volumen final (exacto)",
        f"{df1['V exacto (m³)'].iloc[-1]:,.1f} m³",
    )

    st.subheader("Diagnóstico del reservorio")

    if V0 <= Vc:
        st.error(
            "El reservorio comienza en el nivel mínimo o por debajo de él. "
            "La comunidad ya se encuentra en una situación crítica."
        )

    elif v_inf < Vc:
        st.error(
            "Situación crítica: el volumen de equilibrio está por debajo "
            "del umbral mínimo. Según el modelo, el reservorio terminará "
            "descendiendo por debajo del nivel requerido."
        )

    elif abs(v_inf - Vc) < 1e-9:
        st.warning(
            "Situación límite: el volumen de equilibrio coincide con el "
            "umbral. El reservorio se aproxima a ese nivel, pero no lo "
            "supera en equilibrio."
        )

    else:
        st.success(
            "Situación favorable: el volumen de equilibrio está por encima "
            "del umbral mínimo. Según el modelo, el reservorio puede "
            "mantenerse por encima del nivel crítico."
        )
    st.subheader(f"Resultados con h₁ = {h:g} días")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.pyplot(grafica_curvas(df1, "Solución analítica vs Heun vs RK4"))
    with col_g2:
        st.pyplot(grafica_errores(df1, "Error absoluto frente a la solución analítica"))

    st.markdown("**Tabla comparativa por pasos**")
    st.dataframe(df1.style.format(COLUMNAS_DECIMALES), width="stretch", hide_index=True)

    st.markdown("**Resumen de errores**")
    resumen_df = pd.DataFrame(
        {
            "Método": ["Heun", "RK4"],
            "Error abs. máx. (m³)": [res1["Heun"]["max_abs"], res1["RK4"]["max_abs"]],
            "Error rel. máx. (%)": [res1["Heun"]["max_rel"], res1["RK4"]["max_rel"]],
            "Error abs. final (m³)": [res1["Heun"]["final_abs"], res1["RK4"]["final_abs"]],
            "Error rel. final (%)": [res1["Heun"]["final_rel"], res1["RK4"]["final_rel"]],
        }
    )
    st.dataframe(
        resumen_df.style.format(
            {c: "{:.6f}" for c in resumen_df.columns if c != "Método"}
        ),
        width="stretch",
        hide_index=True,
    )
    mejor = "RK4" if res1["RK4"]["max_abs"] < res1["Heun"]["max_abs"] else "Heun"
    st.info(f"Con h₁ = {h:g} días, el método con menor error máximo fue **{mejor}**.")

    st.subheader("Interpretación para la comunidad")
    st.write(texto_interp)

    st.subheader("Guardar informe")
    titulo_informe = st.text_input("Título del informe (opcional)", max_chars=80)
    cg1, cg2, cg3 = st.columns(3)
    if cg1.button("💾 Guardar en la base de datos"):
        nuevo_id = db.guardar_informe(
            titulo_informe,
            V0,
            a,
            k,
            h,
            T,
            Vc,
            t_umbral,
            a_min,
            res1["Heun"]["max_abs"],
            res1["RK4"]["max_abs"],
            texto_interp,
            df1,
        )
        st.success(f"Informe #{nuevo_id} guardado. Búscalo en la pestaña «Historial de informes».")
    cg2.download_button(
        "⬇️ Descargar informe (.md)",
        data=informe_markdown(),
        file_name="informe_reservorio.md",
        mime="text/markdown",
    )
    cg3.download_button(
        "⬇️ Descargar tabla (.csv)",
        data=df1.to_csv(index=False),
        file_name="tabla_reservorio.csv",
        mime="text/csv",
    )

# ---- Comparación de pasos -------------------------------------------------
with tab_comp:
    st.subheader(f"Comparación entre h₁ = {h:g} y h₂ = {h2:g} días")
    comp = pd.DataFrame(
        {
            "h (días)": [h, h, h2, h2],
            "Método": ["Heun", "RK4", "Heun", "RK4"],
            "Error abs. máx. (m³)": [
                res1["Heun"]["max_abs"],
                res1["RK4"]["max_abs"],
                res2["Heun"]["max_abs"],
                res2["RK4"]["max_abs"],
            ],
            "Error rel. máx. (%)": [
                res1["Heun"]["max_rel"],
                res1["RK4"]["max_rel"],
                res2["Heun"]["max_rel"],
                res2["RK4"]["max_rel"],
            ],
        }
    )
    st.dataframe(
        comp.style.format(
            {
                "h (días)": "{:g}",
                "Error abs. máx. (m³)": "{:.8f}",
                "Error rel. máx. (%)": "{:.8f}",
            }
        ),
        width="stretch",
        hide_index=True,
    )
    cc1, cc2 = st.columns(2)
    with cc1:
        st.pyplot(grafica_curvas(df1, f"h₁ = {h:g} días"))
    with cc2:
        st.pyplot(grafica_curvas(df2, f"h₂ = {h2:g} días"))
    st.markdown(
        "Al reducir h, el error de ambos métodos disminuye. Heun es de orden 2 "
        "(el error baja aproximadamente con h²) y RK4 es de orden 4 (aproximadamente con h⁴), "
        "por eso RK4 suele ser mucho más preciso con el mismo paso."
    )
    with st.expander(f"Ver tabla completa con h₂ = {h2:g} días"):
        st.dataframe(df2.style.format(COLUMNAS_DECIMALES), width="stretch", hide_index=True)

# ---- Solución analítica ---------------------------------------------------
with tab_teoria:
    st.subheader("Solución analítica de la EDO")
    st.markdown("EDO lineal de primer orden con condición inicial:")
    st.latex(r"\frac{dV}{dt} = a - kV, \qquad V(0)=V_0")
    st.markdown("Reescribimos como `dV/dt + kV = a` y usamos el factor integrante `e^{kt}`:")
    st.latex(r"\frac{d}{dt}\left(V e^{kt}\right) = a e^{kt} \;\Rightarrow\; V e^{kt} = \frac{a}{k}e^{kt} + C")
    st.latex(r"V(t) = \frac{a}{k} + C e^{-kt}, \qquad C = V_0 - \frac{a}{k}")
    st.latex(r"\boxed{V(t) = \frac{a}{k} + \left(V_0 - \frac{a}{k}\right)e^{-kt}}")

    st.markdown("**Verificación por sustitución**")
    st.latex(r"V'(t) = -k\left(V_0-\tfrac{a}{k}\right)e^{-kt}")
    st.latex(r"a - kV(t) = a - a - k\left(V_0-\tfrac{a}{k}\right)e^{-kt} = V'(t) \;\checkmark")
    st.latex(r"V(0) = \tfrac{a}{k} + V_0 - \tfrac{a}{k} = V_0 \;\checkmark")

    st.markdown("**Tiempo hasta el umbral** (si `V₀ > V_c > a/k`):")
    st.latex(r"t^* = \frac{1}{k}\ln\!\left(\frac{V_0 - a/k}{V_c - a/k}\right)")
    st.markdown("**Aporte mínimo para sostener el umbral:**")
    st.latex(r"a_{\min} = k\,V_c")

    st.markdown("**Métodos numéricos usados** (con `f(V) = a − kV`):")
    st.latex(r"\text{Heun: } V^* = V_n + h f(V_n),\quad V_{n+1} = V_n + \tfrac{h}{2}\left[f(V_n)+f(V^*)\right]")
    st.latex(
        r"\text{RK4: } V_{n+1} = V_n + \tfrac{h}{6}\left(k_1+2k_2+2k_3+k_4\right)"
    )
    st.latex(
        r"k_1=f(V_n),\; k_2=f(V_n+\tfrac{h}{2}k_1),\; k_3=f(V_n+\tfrac{h}{2}k_2),\; k_4=f(V_n+h k_3)"
    )

# ---- Historial ------------------------------------------------------------
with tab_hist:
    st.subheader("Informes guardados")
    informes = db.listar_informes()
    if not informes:
        st.info("Aún no hay informes guardados. Ejecuta una simulación y pulsa «Guardar».")
    else:
        lista = pd.DataFrame(informes).rename(
            columns={
                "id": "ID",
                "fecha": "Fecha (hora Bolivia)",
                "titulo": "Título",
                "v0": "V₀ (m³)",
                "a": "a (m³/día)",
                "k": "k (1/día)",
                "h": "h (días)",
                "t_final": "T (días)",
                "v_umbral": "Umbral (m³)",
                "t_umbral": "Días al umbral",
                "err_max_heun": "Err. máx. Heun (m³)",
                "err_max_rk4": "Err. máx. RK4 (m³)",
            }
        )
        st.dataframe(lista, width="stretch", hide_index=True)

        elegido = st.selectbox("Abrir informe", [i["id"] for i in informes])
        inf = db.obtener_informe(elegido)
        if inf:
            st.markdown(f"**Informe #{inf['id']}** · {inf['fecha']} · {inf['titulo'] or 'Sin título'}")
            st.write(
                f"V₀ = {inf['v0']:,.2f} m³ · a = {inf['a']:,.2f} m³/día · "
                f"k = {inf['k']:.4f} 1/día · h = {inf['h']:g} días · "
                f"T = {inf['t_final']:,.1f} días · umbral = {inf['v_umbral']:,.2f} m³"
            )
            st.write(inf["interpretacion"])
            st.dataframe(pd.DataFrame(inf["tabla"]), width="stretch", hide_index=True)
