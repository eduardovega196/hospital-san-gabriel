"""
bbdd.py - Generador de Base de Datos de Insumos Hospitalarios
Genera 2.000 registros ficticios con datos realistas para el sistema de gestión.
Uso: python bbdd.py
"""

import pandas as pd
import numpy as np
import sqlite3
import random
from datetime import datetime, timedelta
import os

# ─────────────────────────────────────────────
# SEED PARA REPRODUCIBILIDAD
# ─────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# DATOS MAESTROS
# ─────────────────────────────────────────────

PRODUCTOS = {
    "Fármaco": [
        ("Paracetamol 500mg", 200, 50),
        ("Paracetamol 1g IV", 150, 30),
        ("Ibuprofeno 400mg", 300, 60),
        ("Amoxicilina 500mg", 250, 50),
        ("Cloxacilina 500mg", 200, 40),
        ("Cefazolina 1g IV", 180, 40),
        ("Metronidazol 500mg", 220, 50),
        ("Ciprofloxacino 500mg", 150, 30),
        ("Omeprazol 20mg", 400, 80),
        ("Ranitidina 150mg", 300, 60),
        ("Metoclopramida 10mg", 250, 50),
        ("Ondansetrón 4mg IV", 120, 30),
        ("Ketoprofeno 100mg IV", 160, 40),
        ("Morfina 10mg IM", 80, 20),
        ("Tramadol 50mg", 200, 40),
        ("Fentanilo 0.05mg IV", 60, 15),
        ("Midazolam 5mg IV", 70, 15),
        ("Propofol 200mg IV", 50, 10),
        ("Ketamina 500mg IV", 40, 10),
        ("Atropina 0.5mg IV", 100, 25),
        ("Adrenalina 1mg IV", 90, 20),
        ("Heparina 5000UI", 180, 40),
        ("Enoxaparina 40mg", 200, 50),
        ("Warfarina 5mg", 150, 30),
        ("Aspirina 100mg", 400, 80),
        ("Atorvastatina 20mg", 300, 60),
        ("Metformina 850mg", 250, 50),
        ("Insulina NPH 100UI/ml", 80, 20),
        ("Insulina Rápida 100UI/ml", 80, 20),
        ("Furosemida 40mg", 200, 40),
        ("Hidrocortisona 100mg IV", 120, 30),
        ("Dexametasona 4mg IV", 130, 30),
        ("Prednisona 5mg", 200, 40),
        ("Salbutamol inhalador", 100, 25),
        ("Budesonida inhalador", 80, 20),
        ("Amiodarona 150mg IV", 60, 15),
        ("Digoxina 0.25mg", 100, 25),
        ("Captopril 25mg", 200, 40),
        ("Losartán 50mg", 250, 50),
        ("Amlodipino 5mg", 220, 45),
        ("Clonazepam 0.5mg", 150, 30),
        ("Lorazepam 2mg IV", 80, 20),
        ("Haloperidol 5mg", 100, 25),
        ("Tramadol 100mg IV", 120, 30),
        ("Dipirona 1g IV", 200, 40),
        ("Ketorolaco 30mg IV", 150, 30),
        ("Vitamina C 1g IV", 180, 40),
        ("Complejo B IV", 120, 30),
        ("Albúmina 20% 100ml", 30, 8),
        ("Manitol 20% 250ml", 50, 12),
    ],
    "Insumo Quirúrgico": [
        ("Sutura Seda 2-0", 150, 30),
        ("Sutura Seda 3-0", 150, 30),
        ("Sutura Vicryl 0", 180, 40),
        ("Sutura Vicryl 2-0", 180, 40),
        ("Sutura Vicryl 3-0", 180, 40),
        ("Sutura Prolene 2-0", 120, 25),
        ("Sutura Prolene 3-0", 120, 25),
        ("Sutura Monocryl 3-0", 100, 20),
        ("Sutura Nylon 2-0", 130, 25),
        ("Sutura Nylon 3-0", 130, 25),
        ("Jeringa 1cc", 500, 100),
        ("Jeringa 3cc", 500, 100),
        ("Jeringa 5cc", 400, 80),
        ("Jeringa 10cc", 400, 80),
        ("Jeringa 20cc", 300, 60),
        ("Jeringa 50cc", 200, 40),
        ("Aguja 21G", 600, 120),
        ("Aguja 23G", 600, 120),
        ("Aguja 25G", 500, 100),
        ("Catéter IV 18G", 300, 60),
        ("Catéter IV 20G", 300, 60),
        ("Catéter IV 22G", 250, 50),
        ("Catéter IV 24G", 200, 40),
        ("Bajada de suero macro", 400, 80),
        ("Bajada de suero micro", 300, 60),
        ("Bajada con filtro", 200, 40),
        ("Suero Fisiológico 9% 250ml", 300, 60),
        ("Suero Fisiológico 9% 500ml", 400, 80),
        ("Suero Fisiológico 9% 1000ml", 400, 80),
        ("Suero Glucosado 5% 500ml", 300, 60),
        ("Suero Glucosado 5% 1000ml", 300, 60),
        ("Ringer Lactato 500ml", 250, 50),
        ("Mascarilla N95", 200, 50),
        ("Mascarilla Quirúrgica", 500, 100),
        ("Guante Latex 6.5", 400, 80),
        ("Guante Latex 7.0", 400, 80),
        ("Guante Latex 7.5", 400, 80),
        ("Guante Nitrilo M", 600, 120),
        ("Guante Nitrilo L", 600, 120),
        ("Gasa Estéril 10x10cm", 500, 100),
        ("Apósito Tegaderm 10x12cm", 200, 40),
        ("Apósito Mepore 9x10cm", 300, 60),
        ("Vendaje Elástico 5cm", 200, 40),
        ("Vendaje Elástico 10cm", 200, 40),
        ("Esparadrapo 5x5cm", 300, 60),
        ("Tela adhesiva hipo.", 200, 40),
        ("Bisturí N°10", 300, 60),
        ("Bisturí N°15", 300, 60),
        ("Bisturí N°22", 200, 40),
        ("Campo estéril 60x60cm", 200, 40),
    ],
    "Implante": [
        ("Tornillo cortical 3.5mm x 26mm", 30, 8),
        ("Tornillo cortical 3.5mm x 30mm", 30, 8),
        ("Tornillo esponjoso 6.5mm x 50mm", 25, 6),
        ("Placa DCP 4 orificios", 20, 5),
        ("Placa DCP 6 orificios", 20, 5),
        ("Placa DCP 8 orificios", 15, 4),
        ("Clavo endomedular tibial", 15, 4),
        ("Clavo endomedular femoral", 15, 4),
        ("Prótesis cadera total", 10, 3),
        ("Prótesis cadera parcial", 10, 3),
        ("Prótesis rodilla total", 8, 2),
        ("Malla hernia 15x15cm", 25, 6),
        ("Malla hernia 10x15cm", 25, 6),
        ("Clip metálico hemo. M", 50, 12),
        ("Clip metálico hemo. L", 50, 12),
        ("Grapa circular 25mm", 20, 5),
        ("Grapa circular 29mm", 20, 5),
        ("Grapa lineal 60mm", 20, 5),
        ("Carga lineal 45mm", 30, 8),
        ("Banda gástrica ajustable", 8, 2),
    ],
}

UBICACIONES = ["Bodega Central", "Pabellón 1", "Pabellón 2", "Pabellón 3", "Urgencias", "UCI"]

PROVEEDORES = [
    "CENABAST", "Laboratorio Chile", "Bayer Chile", "Pfizer Chile",
    "Roche Chile", "Abbott Chile", "Johnson & Johnson", "Medtronic",
    "Fresenius Kabi", "B. Braun", "Synthes Chile", "Stryker Chile",
]


def generar_fecha_vencimiento(categoria: str) -> datetime:
    """
    Genera fechas de vencimiento realistas según categoría.
    ~15% de los productos vencidos o próximos a vencer (< 30 días).
    """
    hoy = datetime.now()
    r = random.random()

    if categoria == "Fármaco":
        if r < 0.07:      # 7% vencidos
            return hoy - timedelta(days=random.randint(1, 180))
        elif r < 0.15:    # 8% vencen en < 30 días
            return hoy + timedelta(days=random.randint(1, 29))
        elif r < 0.30:    # 15% vencen en 30-60 días
            return hoy + timedelta(days=random.randint(30, 60))
        else:             # 70% ok
            return hoy + timedelta(days=random.randint(61, 730))

    elif categoria == "Insumo Quirúrgico":
        if r < 0.05:
            return hoy - timedelta(days=random.randint(1, 90))
        elif r < 0.13:
            return hoy + timedelta(days=random.randint(1, 29))
        elif r < 0.28:
            return hoy + timedelta(days=random.randint(30, 60))
        else:
            return hoy + timedelta(days=random.randint(61, 1095))

    else:  # Implante
        if r < 0.03:
            return hoy - timedelta(days=random.randint(1, 60))
        elif r < 0.10:
            return hoy + timedelta(days=random.randint(1, 29))
        elif r < 0.20:
            return hoy + timedelta(days=random.randint(30, 60))
        else:
            return hoy + timedelta(days=random.randint(61, 1825))


def generar_lote() -> str:
    año = random.randint(2023, 2025)
    mes = random.randint(1, 12)
    seq = random.randint(1000, 9999)
    return f"LOT-{año}{mes:02d}-{seq}"


def calcular_estado_vencimiento(fecha_venc: datetime) -> str:
    hoy = datetime.now()
    diff = (fecha_venc - hoy).days
    if diff < 0:
        return "VENCIDO"
    elif diff <= 30:
        return "CRÍTICO"
    elif diff <= 60:
        return "ALERTA"
    else:
        return "OK"


def calcular_estado_stock(stock_actual: int, stock_minimo: int) -> str:
    ratio = stock_actual / stock_minimo if stock_minimo > 0 else 1
    if stock_actual == 0:
        return "AGOTADO"
    elif ratio < 1.0:
        return "CRÍTICO"
    elif ratio < 1.5:
        return "BAJO"
    else:
        return "NORMAL"


def generar_historial_uso(id_insumo: int, n_semanas: int = 12) -> list[dict]:
    """Genera historial de consumo semanal para proyección predictiva."""
    registros = []
    hoy = datetime.now()
    consumo_base = random.randint(5, 80)
    tendencia = random.uniform(-0.5, 2.0)  # puede subir o bajar

    for semana in range(n_semanas, 0, -1):
        fecha = hoy - timedelta(weeks=semana)
        ruido = random.uniform(0.7, 1.3)
        consumo = max(0, int((consumo_base + tendencia * (n_semanas - semana)) * ruido))
        registros.append({
            "ID_Insumo": id_insumo,
            "Fecha_Semana": fecha.strftime("%Y-%m-%d"),
            "Consumo_Unidades": consumo,
        })
    return registros


def generar_base_de_datos(n_registros: int = 2000, db_path: str = "hospital_insumos.db"):
    print("=" * 60)
    print("  GENERADOR DE BASE DE DATOS - SISTEMA HOSPITALARIO")
    print("=" * 60)
    print(f"\n[1/4] Generando {n_registros} registros de insumos...")

    # ─── Construir pool de productos ───────────────────────────────
    pool = []
    for categoria, productos in PRODUCTOS.items():
        for nombre, stock_max, stock_min in productos:
            pool.append((nombre, categoria, stock_max, stock_min))

    registros_insumos = []
    registros_historial = []
    id_counter = 1

    while len(registros_insumos) < n_registros:
        nombre, categoria, stock_max, stock_min = random.choice(pool)
        ubicacion = random.choice(UBICACIONES)
        fecha_venc = generar_fecha_vencimiento(categoria)
        stock_actual = random.randint(0, stock_max)
        lote = generar_lote()
        proveedor = random.choice(PROVEEDORES)
        precio_unit = round(random.uniform(100, 150000), 0)

        estado_venc = calcular_estado_vencimiento(fecha_venc)
        estado_stock = calcular_estado_stock(stock_actual, stock_min)

        registros_insumos.append({
            "ID_Insumo":          id_counter,
            "Nombre_Producto":    nombre,
            "Categoria":          categoria,
            "Lote":               lote,
            "Proveedor":          proveedor,
            "Fecha_Vencimiento":  fecha_venc.strftime("%Y-%m-%d"),
            "Stock_Actual":       stock_actual,
            "Stock_Minimo":       stock_min,
            "Precio_Unitario":    precio_unit,
            "Ubicacion":          ubicacion,
            "Estado_Vencimiento": estado_venc,
            "Estado_Stock":       estado_stock,
            "Fecha_Ingreso":      (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        })

        # Historial de uso para módulo predictivo (sólo muestra de 400 productos)
        if id_counter <= 400:
            registros_historial.extend(generar_historial_uso(id_counter))

        id_counter += 1

    df_insumos = pd.DataFrame(registros_insumos)
    df_historial = pd.DataFrame(registros_historial)

    print(f"    ✓ {len(df_insumos)} registros de insumos generados")
    print(f"    ✓ {len(df_historial)} registros de historial de consumo generados")

    # ─── Estadísticas de distribución ──────────────────────────────
    print("\n[2/4] Estadísticas de la base generada:")
    for cat, cnt in df_insumos["Categoria"].value_counts().items():
        print(f"    • {cat}: {cnt} registros")
    print()
    for est, cnt in df_insumos["Estado_Vencimiento"].value_counts().items():
        pct = cnt / len(df_insumos) * 100
        print(f"    • Vencimiento {est}: {cnt} ({pct:.1f}%)")
    print()
    for est, cnt in df_insumos["Estado_Stock"].value_counts().items():
        pct = cnt / len(df_insumos) * 100
        print(f"    • Stock {est}: {cnt} ({pct:.1f}%)")

    # ─── Guardar en SQLite ──────────────────────────────────────────
    print(f"\n[3/4] Guardando en base de datos SQLite: {db_path} ...")
    conn = sqlite3.connect(db_path)

    df_insumos.to_sql("insumos", conn, if_exists="replace", index=False)
    df_historial.to_sql("historial_consumo", conn, if_exists="replace", index=False)

    # Tabla de movimientos (traslados entre bodegas)
    movimientos = []
    for _ in range(500):
        row = df_insumos.sample(1).iloc[0]
        movimientos.append({
            "ID_Movimiento": _ + 1,
            "ID_Insumo":     row["ID_Insumo"],
            "Nombre":        row["Nombre_Producto"],
            "Lote":          row["Lote"],
            "Tipo":          random.choice(["Entrada", "Salida", "Traslado"]),
            "Cantidad":      random.randint(1, 50),
            "Origen":        random.choice(UBICACIONES),
            "Destino":       random.choice(UBICACIONES),
            "Fecha":         (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d %H:%M"),
            "Usuario":       random.choice(["Dr. Eduardo Vega", "Dr. Félix Fauré", "Klga. Jessica Berton", "Farm. Christian Norambuena", "Enf. Claudia Manquelipe"]),
            "Motivo":        "",
        })
    pd.DataFrame(movimientos).to_sql("movimientos", conn, if_exists="replace", index=False)

    conn.close()
    print(f"    ✓ Base de datos guardada correctamente")

    # ─── Exportar también a CSV ─────────────────────────────────────
    csv_path = "insumos_hospital.csv"
    df_insumos.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"    ✓ CSV exportado: {csv_path}")

    print("\n[4/4] ¡Base de datos lista!")
    print(f"\n  Archivos generados:")
    print(f"    • {db_path}  (SQLite — usado por app.py)")
    print(f"    • {csv_path}  (respaldo CSV)")
    print("=" * 60)

    return df_insumos


# ─────────────────────────────────────────────
# FUNCIONES DE ACCESO (usadas por app.py)
# ─────────────────────────────────────────────

DB_PATH = "hospital_insumos.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def cargar_insumos() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM insumos", conn)
    conn.close()
    return df


def cargar_historial() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM historial_consumo", conn)
    conn.close()
    return df


def cargar_movimientos() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM movimientos ORDER BY Fecha DESC", conn)
    conn.close()
    return df


def cargar_consumo_combinado() -> pd.DataFrame:
    """
    Historial de consumo semanal para la proyección predictiva, combinando:
      · la base histórica (historial_consumo), como piso para que el módulo
        siempre tenga datos suficientes para proyectar, y
      · las SALIDAS reales registradas en movimientos (consumo verdadero del
        hospital), agregadas por semana.
    Si una misma semana aparece en ambas fuentes, los consumos se suman.
    Devuelve columnas: ID_Insumo, Fecha_Semana, Consumo_Unidades.
    """
    conn = get_connection()
    hist = pd.read_sql(
        "SELECT ID_Insumo, Fecha_Semana, Consumo_Unidades FROM historial_consumo",
        conn
    )
    try:
        mov = pd.read_sql(
            "SELECT ID_Insumo, Cantidad, Fecha FROM movimientos WHERE Tipo = 'Salida'",
            conn
        )
    except Exception:
        mov = pd.DataFrame(columns=["ID_Insumo", "Cantidad", "Fecha"])
    conn.close()

    frames = [hist]

    if len(mov) > 0:
        mov["Fecha_dt"] = pd.to_datetime(mov["Fecha"], errors="coerce")
        mov = mov.dropna(subset=["Fecha_dt"])
        if len(mov) > 0:
            # Normalizar al lunes de cada semana
            mov["Fecha_Semana"] = (
                mov["Fecha_dt"] - pd.to_timedelta(mov["Fecha_dt"].dt.weekday, unit="D")
            ).dt.strftime("%Y-%m-%d")
            salidas_sem = (
                mov.groupby(["ID_Insumo", "Fecha_Semana"])["Cantidad"]
                .sum().reset_index()
                .rename(columns={"Cantidad": "Consumo_Unidades"})
            )
            frames.append(salidas_sem)

    combinado = pd.concat(frames, ignore_index=True)
    # Sumar cuando una misma semana proviene de ambas fuentes
    combinado = (
        combinado.groupby(["ID_Insumo", "Fecha_Semana"])["Consumo_Unidades"]
        .sum().reset_index()
    )
    return combinado


def _asegurar_columna_motivo(cursor):
    """Garantiza que la tabla movimientos tenga la columna Motivo.
    Permite que bases de datos antiguas (sin la columna) sigan funcionando."""
    cursor.execute("PRAGMA table_info(movimientos)")
    columnas = [c[1] for c in cursor.fetchall()]
    if "Motivo" not in columnas:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN Motivo TEXT DEFAULT ''")


def _recalcular_estado_stock(cursor, id_insumo: int):
    """Recalcula y guarda el Estado_Stock de un registro según su stock actual."""
    cursor.execute(
        "SELECT Stock_Actual, Stock_Minimo FROM insumos WHERE ID_Insumo = ?",
        (id_insumo,)
    )
    row = cursor.fetchone()
    if row:
        nuevo_estado = calcular_estado_stock(row[0], row[1])
        cursor.execute(
            "UPDATE insumos SET Estado_Stock = ? WHERE ID_Insumo = ?",
            (nuevo_estado, id_insumo)
        )


def registrar_movimiento(id_insumo: int, nombre: str, lote: str,
                         tipo: str, cantidad: int,
                         origen: str, destino: str, usuario: str,
                         motivo: str = ""):
    """
    Registra un nuevo movimiento y ajusta el stock según el tipo:
      · Salida   → descuenta del registro de origen (se consume).
      · Entrada  → suma al registro indicado (llega mercadería).
      · Traslado → descuenta del origen y suma al destino. Si el mismo
                   producto+lote no existe en el destino, crea una fila nueva
                   (traslado parcial, opción B).
    """
    conn = get_connection()
    cursor = conn.cursor()
    _asegurar_columna_motivo(cursor)

    # 1) Registrar el movimiento en el historial
    cursor.execute("SELECT COALESCE(MAX(ID_Movimiento), 0) + 1 FROM movimientos")
    next_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO movimientos
        (ID_Movimiento, ID_Insumo, Nombre, Lote, Tipo, Cantidad, Origen, Destino, Fecha, Usuario, Motivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        next_id, id_insumo, nombre, lote, tipo, cantidad,
        origen, destino,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        usuario, motivo,
    ))

    # 2) Ajustar el stock según el tipo
    if tipo == "Salida":
        cursor.execute(
            "UPDATE insumos SET Stock_Actual = MAX(0, Stock_Actual - ?) WHERE ID_Insumo = ?",
            (cantidad, id_insumo)
        )
        _recalcular_estado_stock(cursor, id_insumo)

    elif tipo == "Entrada":
        cursor.execute(
            "UPDATE insumos SET Stock_Actual = Stock_Actual + ? WHERE ID_Insumo = ?",
            (cantidad, id_insumo)
        )
        _recalcular_estado_stock(cursor, id_insumo)

    elif tipo == "Traslado" and origen != destino:
        # 2a) Descontar del registro de origen
        cursor.execute(
            "UPDATE insumos SET Stock_Actual = MAX(0, Stock_Actual - ?) WHERE ID_Insumo = ?",
            (cantidad, id_insumo)
        )
        _recalcular_estado_stock(cursor, id_insumo)

        # 2b) Buscar el mismo producto+lote ya existente en el destino
        cursor.execute("""
            SELECT ID_Insumo FROM insumos
            WHERE Nombre_Producto = ? AND Lote = ? AND Ubicacion = ?
            LIMIT 1
        """, (nombre, lote, destino))
        fila_destino = cursor.fetchone()

        if fila_destino:
            # Ya existe en el destino → sumar
            dest_id = fila_destino[0]
            cursor.execute(
                "UPDATE insumos SET Stock_Actual = Stock_Actual + ? WHERE ID_Insumo = ?",
                (cantidad, dest_id)
            )
            _recalcular_estado_stock(cursor, dest_id)
        else:
            # No existe → crear fila nueva en el destino, copiando datos del origen
            cursor.execute("""
                SELECT Categoria, Proveedor, Fecha_Vencimiento,
                       Stock_Minimo, Precio_Unitario, Fecha_Ingreso
                FROM insumos WHERE ID_Insumo = ?
            """, (id_insumo,))
            o = cursor.fetchone()
            if o:
                categoria, proveedor, fecha_venc, stock_min, precio, fecha_ing = o
                cursor.execute("SELECT COALESCE(MAX(ID_Insumo), 0) + 1 FROM insumos")
                nuevo_id = cursor.fetchone()[0]
                estado_venc  = calcular_estado_vencimiento(
                    datetime.strptime(fecha_venc, "%Y-%m-%d")
                )
                estado_stock = calcular_estado_stock(cantidad, stock_min)
                cursor.execute("""
                    INSERT INTO insumos
                    (ID_Insumo, Nombre_Producto, Categoria, Lote, Proveedor,
                     Fecha_Vencimiento, Stock_Actual, Stock_Minimo, Precio_Unitario,
                     Ubicacion, Estado_Vencimiento, Estado_Stock, Fecha_Ingreso)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    nuevo_id, nombre, categoria, lote, proveedor, fecha_venc,
                    cantidad, stock_min, precio, destino,
                    estado_venc, estado_stock, fecha_ing,
                ))

    conn.commit()
    conn.close()


def registrar_ajuste(id_insumo: int, nombre: str, lote: str, ubicacion: str,
                     stock_anterior: int, stock_nuevo: int,
                     motivo: str, usuario: str):
    """
    Registra un ajuste manual de stock como movimiento trazable tipo 'Ajuste'.
    NO modifica el stock: se asume que el formulario de edición ya fijó el
    valor nuevo. Solo deja la huella de quién, cuándo, cuánto y por qué.
    Si el stock no cambió, no hace nada.
    """
    if int(stock_anterior) == int(stock_nuevo):
        return

    conn = get_connection()
    cursor = conn.cursor()
    _asegurar_columna_motivo(cursor)

    cursor.execute("SELECT COALESCE(MAX(ID_Movimiento), 0) + 1 FROM movimientos")
    next_id = cursor.fetchone()[0]

    delta       = int(stock_nuevo) - int(stock_anterior)
    motivo_full = f"{motivo} (de {stock_anterior} a {stock_nuevo})"

    cursor.execute("""
        INSERT INTO movimientos
        (ID_Movimiento, ID_Insumo, Nombre, Lote, Tipo, Cantidad, Origen, Destino, Fecha, Usuario, Motivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        next_id, id_insumo, nombre, lote, "Ajuste", abs(delta),
        ubicacion, ubicacion,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        usuario, motivo_full,
    ))

    conn.commit()
    conn.close()


def get_kpis() -> dict:
    """Devuelve KPIs principales para el dashboard."""
    df = cargar_insumos()
    return {
        "total_insumos":    len(df),
        "stock_critico":    len(df[df["Estado_Stock"].isin(["CRÍTICO", "AGOTADO"])]),
        "por_vencer_30":    len(df[df["Estado_Vencimiento"] == "CRÍTICO"]),
        "vencidos":         len(df[df["Estado_Vencimiento"] == "VENCIDO"]),
        "alerta_60":        len(df[df["Estado_Vencimiento"] == "ALERTA"]),
        "valor_total":      (df["Stock_Actual"] * df["Precio_Unitario"]).sum(),
    }


# ─────────────────────────────────────────────
# EJECUTAR GENERADOR SI SE LLAMA DIRECTAMENTE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        generar_base_de_datos(n_registros=2000)
    else:
        resp = input(f"\nLa base de datos '{DB_PATH}' ya existe. ¿Regenerar? [s/N]: ").strip().lower()
        if resp == "s":
            os.remove(DB_PATH)
            generar_base_de_datos(n_registros=2000)
        else:
            print("Base de datos existente conservada.")