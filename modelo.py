"""
Modelo matemático: reservorio comunitario de agua en sequía (La Paz, Bolivia).

EDO de primer orden con condición inicial:
    dV/dt = a - k*V ,   V(0) = V0

    V(t) : volumen de agua en el reservorio (m³)
    t    : tiempo (días)
    a    : aporte de agua durante la sequía (m³/día)
    k    : tasa de salida por consumo y pérdidas (1/día)

Solución analítica:
    V(t) = a/k + (V0 - a/k) * exp(-k*t)

NOTA: los parámetros usados en la aplicación son HIPOTÉTICOS.
"""
import math

import numpy as np
import pandas as pd

MAX_PASOS = 20000


# ---------------------------------------------------------------------------
# EDO y solución exacta
# ---------------------------------------------------------------------------
def f(V, a, k):
    """Lado derecho de la EDO: dV/dt = a - k*V."""
    return a - k * V


def solucion_analitica(t, V0, a, k):
    """V(t) = a/k + (V0 - a/k) * e^(-k t)."""
    return a / k + (V0 - a / k) * np.exp(-k * t)


# ---------------------------------------------------------------------------
# Métodos numéricos
# ---------------------------------------------------------------------------
def numero_pasos(T, h):
    """Número de pasos para cubrir [0, T] con paso h (redondea hacia arriba)."""
    return max(1, int(math.ceil(T / h - 1e-9)))


def heun(V0, a, k, h, n):
    """Método de Heun (Runge-Kutta de orden 2).

    V*      = V_n + h * f(V_n)                      (predictor de Euler)
    V_{n+1} = V_n + (h/2) * [ f(V_n) + f(V*) ]      (corrector)
    """
    V = np.empty(n + 1)
    V[0] = V0
    for i in range(n):
        f1 = f(V[i], a, k)
        V_pred = V[i] + h * f1
        f2 = f(V_pred, a, k)
        V[i + 1] = V[i] + (h / 2.0) * (f1 + f2)
    return V


def rk4(V0, a, k, h, n):
    """Método clásico de Runge-Kutta de orden 4.

    k1 = f(V_n)
    k2 = f(V_n + h*k1/2)
    k3 = f(V_n + h*k2/2)
    k4 = f(V_n + h*k3)
    V_{n+1} = V_n + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
    """
    V = np.empty(n + 1)
    V[0] = V0
    for i in range(n):
        k1 = f(V[i], a, k)
        k2 = f(V[i] + h * k1 / 2.0, a, k)
        k3 = f(V[i] + h * k2 / 2.0, a, k)
        k4 = f(V[i] + h * k3, a, k)
        V[i + 1] = V[i] + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return V


# ---------------------------------------------------------------------------
# Simulación completa y errores
# ---------------------------------------------------------------------------
def _error_relativo(exacto, absoluto):
    """Error relativo porcentual; NaN cuando el valor exacto es cero."""
    exacto = np.asarray(exacto, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(exacto != 0, absoluto / np.abs(exacto) * 100.0, np.nan)
    return rel


def simular(V0, a, k, h, T):
    """Ejecuta solución analítica, Heun y RK4 con los mismos parámetros y h.

    Devuelve un DataFrame con una fila por paso.
    """
    n = numero_pasos(T, h)
    t = np.arange(n + 1) * h
    exacta = solucion_analitica(t, V0, a, k)
    v_heun = heun(V0, a, k, h, n)
    v_rk4 = rk4(V0, a, k, h, n)

    abs_heun = np.abs(exacta - v_heun)
    abs_rk4 = np.abs(exacta - v_rk4)

    return pd.DataFrame(
        {
            "Paso": np.arange(n + 1),
            "t (días)": t,
            "V exacto (m³)": exacta,
            "V Heun (m³)": v_heun,
            "Error abs. Heun (m³)": abs_heun,
            "Error rel. Heun (%)": _error_relativo(exacta, abs_heun),
            "V RK4 (m³)": v_rk4,
            "Error abs. RK4 (m³)": abs_rk4,
            "Error rel. RK4 (%)": _error_relativo(exacta, abs_rk4),
        }
    )


def resumen_errores(df):
    """Errores máximos y errores en el tiempo final para cada método."""
    out = {}
    for nombre, c_abs, c_rel in (
        ("Heun", "Error abs. Heun (m³)", "Error rel. Heun (%)"),
        ("RK4", "Error abs. RK4 (m³)", "Error rel. RK4 (%)"),
    ):
        out[nombre] = {
            "max_abs": float(df[c_abs].max()),
            "max_rel": float(np.nanmax(df[c_rel].to_numpy())),
            "final_abs": float(df[c_abs].iloc[-1]),
            "final_rel": float(df[c_rel].iloc[-1]),
        }
    return out


# ---------------------------------------------------------------------------
# Preguntas del desafío
# ---------------------------------------------------------------------------
def tiempo_umbral(V0, a, k, Vc):
    """Días en que V(t) baja hasta el umbral Vc (solución exacta).

    t* = (1/k) * ln[ (V0 - a/k) / (Vc - a/k) ]
    Devuelve None si el volumen nunca llega al umbral (Vc <= a/k).
    Devuelve 0.0 si ya se parte en o por debajo del umbral.
    """
    if V0 <= Vc:
        return 0.0
    v_inf = a / k
    if Vc <= v_inf:
        return None
    return math.log((V0 - v_inf) / (Vc - v_inf)) / k


def aporte_minimo(k, Vc):
    """Aporte mínimo (m³/día) para que el equilibrio a/k sea >= Vc."""
    return k * Vc


def interpretacion(V0, a, k, Vc, T, t_umbral):
    """Texto en lenguaje sencillo sobre lo que significan los resultados."""
    v_inf = a / k
    partes = [
        f"Con un volumen inicial de {V0:,.1f} m³, un aporte de {a:,.2f} m³/día "
        f"y una tasa de salida de {k:.4f} 1/día, el reservorio tiende a "
        f"estabilizarse en {v_inf:,.1f} m³ (valor a/k)."
    ]
    if Vc > 0:
        if V0 <= Vc:
            partes.append(
                f"El volumen inicial ya está en o por debajo del umbral de "
                f"{Vc:,.0f} m³: el barrio parte de una situación de riesgo."
            )
        elif t_umbral is None:
            partes.append(
                f"Con estos parámetros el volumen no baja del umbral de "
                f"{Vc:,.0f} m³; se estabiliza en {v_inf:,.1f} m³."
            )
        else:
            texto = (
                f"El volumen baja de {Vc:,.0f} m³ en aproximadamente "
                f"{t_umbral:,.1f} días. Desde ese momento conviene organizar "
                f"turnos de distribución equitativos para evitar tensiones "
                f"entre vecinos."
            )
            if t_umbral > T:
                texto += (
                    f" (Ese momento queda fuera del tiempo simulado de {T:,.0f} días.)"
                )
            partes.append(texto)

        a_min = aporte_minimo(k, Vc)
        if a < a_min:
            partes.append(
                f"Para sostener al menos {Vc:,.0f} m³ se necesitaría un aporte "
                f"de {a_min:,.2f} m³/día o más (faltan {a_min - a:,.2f} m³/día), "
                f"por ejemplo con camión cisterna, o bien reducir k a "
                f"{a / Vc:.4f} 1/día o menos reparando fugas y bajando el consumo."
            )
        else:
            partes.append(
                f"El aporte actual ({a:,.2f} m³/día) alcanza para sostener el "
                f"umbral (mínimo requerido: {a_min:,.2f} m³/día)."
            )
    partes.append(
        "Aviso: los parámetros son hipotéticos y el resultado es una simulación "
        "del modelo, no una predicción comprobada con datos reales."
    )
    return " ".join(partes)
