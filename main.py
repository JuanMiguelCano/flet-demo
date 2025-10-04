import os
import flet as ft

# ------------------------------
# Utilidades de UI
# ------------------------------
def row_label_control(label: str, control: ft.Control):
    return ft.Row([ft.Text(label), control], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

def pill(text: str):
    return ft.Container(
        content=ft.Text(text, size=12, weight="bold"),
        padding=ft.padding.symmetric(6, 8),
        border_radius=999,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

# ------------------------------
# Cálculos de scores
# ------------------------------
def calc_cha2ds2_vasc(values: dict) -> tuple[int, str]:
    age = int(values["age"].value or 0)
    sex = values["sex"].value  # "M" o "F"
    points = 0
    # C(HF) 1
    points += 1 if values["hf"].value else 0
    # H 1
    points += 1 if values["htn"].value else 0
    # A2: >=75 => 2, 65-74 => 1
    if age >= 75:
        points += 2
    elif 65 <= age <= 74:
        points += 1
    # D 1
    points += 1 if values["dm"].value else 0
    # S2 (ictus/TIA/TE previos) 2
    points += 2 if values["stroke_tia_te"].value else 0
    # V (IAM previo, enfermedad arterial periférica o placa aórtica) 1
    points += 1 if values["vascular"].value else 0
    # Sc (sexo femenino) 1
    points += 1 if sex == "F" else 0

    # interpretación (resumen clásico; ten en cuenta cambios de guías recientes)
    if sex == "M":
        rec = "0: bajo; 1: considerar OAC; ≥2: recomendar OAC"
    else:
        rec = "1: bajo; 2: considerar OAC; ≥3: recomendar OAC"
    return points, f"Puntuación: {points}. Recomendación orientativa (ESC): {rec}"

def calc_has_bled(values: dict) -> tuple[int, str]:
    age = int(values["age"].value or 0)
    points = 0
    # H (HTA sistólica >160 mmHg)
    points += 1 if values["sbp160"].value else 0
    # A (renal/liver) 1 punto cada uno
    points += 1 if values["renal"].value else 0
    points += 1 if values["liver"].value else 0
    # S (stroke)
    points += 1 if values["stroke"].value else 0
    # B (bleeding) historia o predisposición
    points += 1 if values["bleeding"].value else 0
    # L (labile INR) — relevante si toma AVK
    points += 1 if values["labile_inr"].value else 0
    # E (elderly) >65
    points += 1 if age > 65 else 0
    # D (drugs/alcohol) 1 punto cada uno
    points += 1 if values["drugs"].value else 0
    points += 1 if values["alcohol"].value else 0

    risk = "bajo" if points <= 2 else "alto (≥3)"
    return points, f"Puntuación: {points}. Riesgo de sangrado {risk}; usar para identificar factores modificables, no para negar OAC por sí solo."

def calc_timi_nstemi(values: dict) -> tuple[int, str]:
    points = 0
    # Criterios TIMI UA/NSTEMI: 7 ítems de 1 punto
    points += 1 if int(values["age"].value or 0) >= 65 else 0
    points += 1 if int(values["cad_risk_factors"].value or 0) >= 3 else 0
    points += 1 if values["known_cad"].value else 0
    points += 1 if values["asa_7d"].value else 0
    points += 1 if values["severe_angina"].value else 0
    points += 1 if values["st_changes"].value else 0
    points += 1 if values["positive_markers"].value else 0

    # Riesgos orientativos (publicación original)
    if points <= 2:
        msg = "Bajo (≈ hasta 8% eventos a 14 días)."
    elif points <= 4:
        msg = "Intermedio (≈ 13–20%)."
    else:
        msg = "Alto (≈ 26–41%)."
    return points, f"Puntuación: {points}. Riesgo {msg} Considerar estrategia invasiva temprana si ≥3 y contexto clínico."

def calc_heart(values: dict) -> tuple[int, str]:
    # Cada componente 0–2
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
    elif points <= 6:
        msg = "Intermedio (≈ ~12–20%)."
    else:
        msg = "Alto (≈ ~50%)."
    return points, f"Puntuación: {points}. Riesgo {msg}"

# ------------------------------
# Formularios por score
# ------------------------------
def form_cha2ds2_vasc(state: dict, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    state["sex"] = ft.Dropdown(label="Sexo", options=[ft.dropdown.Option("M","Masculino"), ft.dropdown.Option("F","Femenino")], value="M", width=180)
    for key, lab in [
        ("hf","Insuficiencia cardiaca"),
        ("htn","Hipertensión"),
        ("dm","Diabetes"),
        ("stroke_tia_te","Ictus/TIA/Tromboembolismo previos"),
        ("vascular","Enfermedad vascular (IAM, EAP, aorta)"),
    ]:
        state[key] = ft.Switch(label=lab, value=False)

    return [
        ft.Text("CHA₂DS₂-VASc", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        row_label_control("Sexo", state["sex"]),
        state["hf"], state["htn"], state["dm"], state["stroke_tia_te"], state["vascular"],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_cha2ds2_vasc(state)))
    ]

def form_has_bled(state: dict, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    switches = {
        "sbp160": "HTA sistólica >160 mmHg",
        "renal": "Enfermedad renal",
        "liver": "Enfermedad hepática",
        "stroke": "Ictus previo",
        "bleeding": "Sangrado mayor previo/predisposición",
        "labile_inr": "INR lábil (si AVK)",
        "drugs": "Fármacos (antiagregantes/NSAIDs)",
        "alcohol": "Alcohol (≥8 U/sem)",
    }
    for k, lab in switches.items():
        state[k] = ft.Switch(label=lab, value=False)

    return [
        ft.Text("HAS-BLED", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        *[state[k] for k in switches.keys()],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_has_bled(state)))
    ]

def form_timi(state: dict, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    state["cad_risk_factors"] = ft.Slider(min=0, max=5, divisions=5, label="{value} factores CAD (tabaco, HTA, dislipemia, DM, FH)", value=0)
    for key, lab in [
        ("known_cad","CAD conocida (estenosis ≥50%)"),
        ("asa_7d","Ácido acetilsalicílico en últimos 7 días"),
        ("severe_angina","≥2 episodios anginosos en 24 h"),
        ("st_changes","Descenso/ascenso ST ≥0.5 mm"),
        ("positive_markers","Marcadores cardiacos positivos"),
    ]:
        state[key] = ft.Switch(label=lab, value=False)

    return [
        ft.Text("TIMI (UA/NSTEMI)", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        state["cad_risk_factors"],
        *[state[k] for k in ["known_cad","asa_7d","severe_angina","st_changes","positive_markers"]],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_timi_nstemi(state)))
    ]

def form_heart(state: dict, on_calc):
    state.clear()
    state["history"] = ft.Dropdown(
        label="Historia clínica",
        options=[ft.dropdown.Option("slight","Leve"), ft.dropdown.Option("moderate","Moderada"), ft.dropdown.Option("high","Altamente sospechosa")],
        value="moderate", width=260
    )
    state["ecg"] = ft.Dropdown(
        label="ECG",
        options=[ft.dropdown.Option("normal","Normal"), ft.dropdown.Option("nonspecific","Alteraciones inespecíficas"), ft.dropdown.Option("st_deviation","Descenso/ascenso ST")],
        value="normal", width=260
    )
    state["age_band"] = ft.Dropdown(
        label="Edad",
        options=[ft.dropdown.Option("lt45","<45"), ft.dropdown.Option("45to64","45–64"), ft.dropdown.Option("ge65","≥65")],
        value="45to64", width=160
    )
    state["riskf"] = ft.Dropdown(
        label="Factores de riesgo (HTA, DM, tabaco, dislipemia, obesidad, FH)",
        options=[ft.dropdown.Option("none","0"), ft.dropdown.Option("one_two","1–2"), ft.dropdown.Option("three_or_more","≥3")],
        value="one_two", width=200
    )
    state["troponin"] = ft.Dropdown(
        label="Troponina",
        options=[ft.dropdown.Option("normal","≤ LSN"), ft.dropdown.Option("1to3x","1–3 × LSN"), ft.dropdown.Option("gt3x",">3 × LSN")],
        value="normal", width=160
    )

    return [
        ft.Text("HEART", size=20, weight="bold"),
        state["history"], state["ecg"], state["age_band"], state["riskf"], state["troponin"],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_heart(state)))
    ]

FORMS = {
    "CHA2DS2-VASc": form_cha2ds2_vasc,
    "HAS-BLED": form_has_bled,
    "TIMI UA/NSTEMI": form_timi,
    "HEART": form_heart,
}

# ------------------------------
# App
# ------------------------------
def main(page: ft.Page):
    page.title = "Calculadoras cardiovasculares"
    page.padding = 16
    page.theme_mode = "light"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Estado compartido entre formularios
    form_state: dict[str, ft.Control] = {}

    # Resultado
    result_title = ft.Text("", size=18, weight="bold")
    result_text = ft.Text("", selectable=True)
    result_row = ft.Column(controls=[result_title, result_text], spacing=6)

    def on_calc(res_tuple):
        score, interp = res_tuple
        result_title.value = f"Resultado: {score}"
        result_text.value = interp
        page.update()

    def render_form(kind: str):
        container.controls.clear()
        # Cabecera chips/ayuda
        help_bar = ft.Row(
            [
                pill("⚠️ Solo apoyo clínico"),
                pill("✅ Introduce datos reales del paciente"),
                pill("🔁 Cambia de score desde el selector"),
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        )
        form_controls = FORMS[kind](form_state, on_calc)
        container.controls.extend([help_bar, ft.Divider(), *form_controls, ft.Divider(), result_row])
        page.update()

    # Selector superior
    selector = ft.Dropdown(
        label="Selecciona calculadora",
        options=[ft.dropdown.Option(k) for k in FORMS.keys()],
        value="CHA2DS2-VASc",
        on_change=lambda e: render_form(selector.value),
        width=260
    )

    container = ft.Column(spacing=10, width=800)
    page.add(ft.Text("🫀 Calculadoras de riesgo", size=26, weight="bold"), selector, container)
    render_form(selector.value)

if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8550))
    )
