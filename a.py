import openpyxl
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Ingreso de Datos"

# ── Fila 1: Estados, Decisiones, Tipo ──
ws.append(["0, 1, 2, 3", "1, 2, 3", "costos"])

# ── Fila vacía ──
ws.append([])

# ── Tabla de Costos ──
ws.append(["Estado", "1", "2", "3"])
ws.append(["0",   0,     "—",  "—"])
ws.append(["1",   1000,  "—",  6000])
ws.append(["2",   3000,  4000, 6000])
ws.append(["3",   "—",   "—",  6000])

# ── Fila vacía ──
ws.append([])

# ── Matrices de Transición ──
def escribir_matriz(ws, decision, filas):
    ws.append([f"Decisión: {decision}"])
    ws.append(["Estado"] + ["0", "1", "2", "3"])
    for origen, probs in filas:
        ws.append([origen] + probs)
    ws.append([])

# Decisión 1
escribir_matriz(ws, "1", [
    ("0", [0, 0.875, 0.0625, 0.0625]),
    ("1", [0, 0.75, 0.125, 0.125]),
    ("2", [0, 0, 0.5, 0.5])
])

# Decisión 2
escribir_matriz(ws, "2", [
    ("2", [0, 1, 0, 0])
])

# Decisión 3
escribir_matriz(ws, "3", [
    ("1", [1, 0, 0, 0]),
    ("2", [1, 0, 0, 0]),
    ("3", [1, 0, 0, 0])
])

wb.save("plantilla_mdp.xlsx")
print("Plantilla generada correctamente.")
