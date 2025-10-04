import os
import flet as ft

# ------------------------------
# Utilidades de UI (sin ft.colors)
# ------------------------------
def row_label_control(label: str, control: ft.Control):
    return ft.Row([ft.Text(label), control], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

def pill(text: str):
    # Color de fondo con hex para evitar ft.colors.*
    return ft.Container(
        content=ft.Text(text, size=12, weight="bold"),
        padding=10,
        border_radius=999,
        bgcolor="#eeeeee",
    )

# ------------------------------
# Cálculos de scores
# ------------------------------
def calc_cha2ds2_vasc(values: dict) -> tuple[int, str]:
    age = int(values["age"].value or 0)
    sex = values["sex"].value  # "M" o "F"
    points = 0
    points += 1 if values["hf"].value else 0              # IC
    points += 1 if values["htn"].value else 0             # HTA
    if age >= 75:                                         # A2
        points += 2
    elif 65 <= age <= 74:
        points += 1
    points += 1 if values["dm"].value else 0              # DM
    points += 2 if values["stroke_tia_te"].value else 0   # Stroke/TIA/TE previos
    points += 1 if values["vascular"].value else 0        # Vascular
    points += 1 if sex == "F" else 0                      # Sexo

    if sex == "M":
        rec = "0: bajo; 1: considerar OAC; ≥2: recomendar OAC"
    else:
        rec = "1: bajo; 2: considerar OAC; ≥3: recomendar OAC"
    return points, f"Puntuación: {points}. Recomendación orientativa (ESC): {rec}"

def calc_has_bled(values: dict) -> tuple[int, str]:
    age = int(values["age"].value or 0)
    points = 0
    points += 1 if values["sbp160"].value else 0
    points += 1 if values["renal"].value else 0
    points += 1 if values["liver"].value else 0
    points += 1 if values["stroke"].value else 0
    points += 1 if values["bleeding"].value else 0
    points += 1 if values["labile_inr"].value else 0
    points += 1 if age > 65 else 0
    points += 1 if values["drugs"].value else 0
    points += 1 if values["alcohol"].value else 0
    risk = "bajo" if points <= 2 else "alto (≥3)"
    return points, f"Puntuación: {points}. Riesgo de sangrado {risk}; identificar factores modificables."

def calc_timi_nstemi(values: dict) -> tuple[int, str]:
    points = 0
    points += 1 if int(values["age"].value or 0) >= 65 else 0
    points += 1 if int(values["cad_risk_factors"].value or 0) >= 3 else 0
    points += 1 if values["known_cad"].value else 0
    points += 1 if values["asa_7d"].value else 0
    points += 1 if values["severe_angina"].value else 0
    points += 1 if values["st_changes"].value else 0
    points += 1 if values["positive_markers"].value else 0
    if points <= 2:
        msg = "Bajo (≈ hasta 8% eventos a 14 días)."
    elif points <= 4:
        msg = "Intermedio (≈ 13–20%)."
    else:
        msg = "Alto (≈ 26–41%)."
    return points, f"Puntuación: {points}. Riesgo {msg}"

def calc_heart(values: dict) -> tuple[int, str]:
    history_map = {"slight": 0, "moderate": 1, "high": 2}
    ecg_map = {"normal": 0, "nonspecific": 1, "st_deviation": 2}
    age_map = {"lt45": 0, "45to64": 1, "ge65": 2}
    rf_map = {"none": 0, "one_two": 1, "three_or_more": 2}
    trop_map = {"normal": 0, "1to3x": 1, "gt3x": 2}

    points = (
        history_map[values["history"].value]
        + ecg_map[values["ecg"].value]
        + age_map[values["age_band"].value]
        + rf_map[values["riskf"].value]
        + trop_map[values["troponin"].value]
    )
    if points <= 3:
        msg = "Bajo (≈ <3% MACE a 6 semanas)."
    el
