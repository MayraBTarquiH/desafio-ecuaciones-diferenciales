"""
Persistencia de informes en SQLite (archivo local `informes.db`).

- Todas las consultas usan parámetros (?) para evitar inyección SQL.
- No se guardan datos personales: solo parámetros, resultados e interpretación.
- En hostings gratuitos el archivo puede reiniciarse; por eso la app también
  ofrece descarga del informe.
"""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone

DB_PATH = os.environ.get(
    "INFORMES_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "informes.db"),
)

# Bolivia (UTC-4, sin horario de verano)
TZ_BOLIVIA = timezone(timedelta(hours=-4))


def _conectar():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(_conectar()) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS informes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                titulo TEXT,
                v0 REAL NOT NULL,
                a REAL NOT NULL,
                k REAL NOT NULL,
                h REAL NOT NULL,
                t_final REAL NOT NULL,
                v_umbral REAL NOT NULL,
                t_umbral REAL,
                aporte_min REAL,
                err_max_heun REAL,
                err_max_rk4 REAL,
                interpretacion TEXT,
                tabla_json TEXT
            )
            """
        )
        con.commit()


def guardar_informe(
    titulo,
    v0,
    a,
    k,
    h,
    t_final,
    v_umbral,
    t_umbral,
    aporte_min,
    err_max_heun,
    err_max_rk4,
    interpretacion,
    tabla_df,
):
    """Guarda un informe y devuelve su id."""
    fecha = datetime.now(TZ_BOLIVIA).strftime("%Y-%m-%d %H:%M:%S")
    tabla_json = tabla_df.to_json(orient="records", force_ascii=False)
    with closing(_conectar()) as con:
        cur = con.execute(
            """
            INSERT INTO informes (
                fecha, titulo, v0, a, k, h, t_final, v_umbral, t_umbral,
                aporte_min, err_max_heun, err_max_rk4, interpretacion, tabla_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fecha,
                (titulo or "").strip()[:80],
                float(v0),
                float(a),
                float(k),
                float(h),
                float(t_final),
                float(v_umbral),
                None if t_umbral is None else float(t_umbral),
                float(aporte_min),
                float(err_max_heun),
                float(err_max_rk4),
                interpretacion,
                tabla_json,
            ),
        )
        con.commit()
        return cur.lastrowid


def listar_informes(limite=200):
    """Lista resumida de informes (más recientes primero)."""
    with closing(_conectar()) as con:
        con.row_factory = sqlite3.Row
        filas = con.execute(
            """
            SELECT id, fecha, titulo, v0, a, k, h, t_final, v_umbral,
                   t_umbral, err_max_heun, err_max_rk4
            FROM informes ORDER BY id DESC LIMIT ?
            """,
            (int(limite),),
        ).fetchall()
    return [dict(f) for f in filas]


def obtener_informe(id_informe):
    """Devuelve un informe completo como diccionario (o None)."""
    with closing(_conectar()) as con:
        con.row_factory = sqlite3.Row
        fila = con.execute(
            "SELECT * FROM informes WHERE id = ?", (int(id_informe),)
        ).fetchone()
    if fila is None:
        return None
    d = dict(fila)
    d["tabla"] = json.loads(d["tabla_json"]) if d.get("tabla_json") else []
    return d
