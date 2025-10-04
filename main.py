import os
import flet as ft

# ----------------- Utilidades UI -----------------
def row_label_control(label: str, control: ft.Control):
    return ft.Row([ft.Text(label), control], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

def pill(text: str):
    return ft.Container(
        content=ft.Text(text, size=12, weight="bold"),
        padding=10,
        border_radius=999,
        bgcolor="#eeeeee",
    )

# ----------------- Cálculos -----------------
def calc_cha2ds2_vasc(values: dict):
    age = int(values["age"].value or 0)
    sex = values["sex"].value  # "M"/"F"
    p = 0
    p += 1 if values["hf"].value else 0
    p += 1 if values["htn"].value else 0
    if age >= 75: p += 2
    elif 65 <= age <= 74: p += 1
    p += 1 if values["dm"].value else 0
    p += 2 if values["stroke_tia_te"].value else 0
    p += 1 if values["vascular"].value else 0
    p += 1 if sex == "F" else 0
    rec = "0: bajo; 1: considerar OAC; ≥2: recomendar OAC" if sex=="M" else "1: bajo; 2: considerar OAC; ≥3: recomendar OAC"
    return p, f"Puntuación: {p}. Recomendación orientativa (ESC): {rec}"

def calc_has_bled(values: dict):
    age = int(values["age"].value or 0)
    p = 0
    p += 1 if values["sbp160"].value else 0
    p += 1 if values["renal"].value else 0
    p += 1 if values["liver"].value else 0
    p += 1 if values["stroke"].value else 0
    p += 1 if values["bleeding"].value else 0
    p += 1 if values["labile_inr"].value else 0
    p += 1 if age > 65 else 0
    p += 1 if values["drugs"].value else 0
    p += 1 if values["alcohol"].value else 0
    risk = "bajo" if p <= 2 else "alto (≥3)"
    return p, f"Puntuación: {p}. Riesgo de sangrado {risk}; identificar factores modificables."

def calc_timi_nstemi(values: dict):
    p = 0
    p += 1 if int(values["age"].value or 0) >= 65 else 0
    p += 1 if int(values["cad_risk_factors"].value or 0) >= 3 else 0
    p += 1 if values["known_cad"].value else 0
    p += 1 if values["asa_7d"].value else 0
    p += 1 if values["severe_angina"].value else 0
    p += 1 if values["st_changes"].value else 0
    p += 1 if values["positive_markers"].value else 0
    if p <= 2: msg = "Bajo (≈ hasta 8% eventos a 14 días)."
    elif p <= 4: msg = "Intermedio (≈ 13–20%)."
    else: msg = "Alto (≈ 26–41%)."
    return p, f"Puntuación: {p}. Riesgo {msg}"

def calc_heart(values: dict):
    history_map = {"slight": 0, "moderate": 1, "high": 2}
    ecg_map = {"normal": 0, "nonspecific": 1, "st_deviation": 2}
    age_map = {"lt45": 0, "45to64": 1, "ge65": 2}
    rf_map = {"none": 0, "one_two": 1, "three_or_more": 2}
    trop_map = {"normal": 0, "1to3x": 1, "gt3x": 2}
    p = (history_map[values["history"].value]
         + ecg_map[values["ecg"].value]
         + age_map[values["age_band"].value]
         + rf_map[values["riskf"].value]
         + trop_map[values["troponin"].value])
    if p <= 3: msg = "Bajo (≈ <3% MACE a 6 semanas)."
    elif p <= 6: msg = "Intermedio (≈ ~12–20%)."
    else: msg = "Alto (≈ ~50%)."
    return p, f"Puntuación: {p}. Riesgo {msg}"

# ----------------- Formularios -----------------
def form_cha2ds2_vasc(state, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    state["sex"] = ft.Dropdown(label="Sexo (M/F)", options=[ft.dropdown.Option("M"), ft.dropdown.Option("F")], value="M", width=160)
    for key, lab in [("hf","Insuficiencia cardiaca"), ("htn","Hipertensión"), ("dm","Diabetes"),
                     ("stroke_tia_te","Ictus/TIA/TE previos"), ("vascular","Enfermedad vascular (IAM, EAP, aorta)")]:
        state[key] = ft.Switch(label=lab, value=False)
    return [
        ft.Text("CHA₂DS₂-VASc", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        row_label_control("Sexo", state["sex"]),
        state["hf"], state["htn"], state["dm"], state["stroke_tia_te"], state["vascular"],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_cha2ds2_vasc(state)))
    ]

def form_has_bled(state, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    for k, lab in {
        "sbp160":"HTA sistólica >160 mmHg","renal":"Enf. renal","liver":"Enf. hepática","stroke":"Ictus previo",
        "bleeding":"Sangrado mayor/predisposición","labile_inr":"INR lábil (si AVK)","drugs":"Fármacos (AAS/NSAIDs)",
        "alcohol":"Alcohol (≥8 U/sem)"
    }.items():
        state[k] = ft.Switch(label=lab, value=False)
    return [
        ft.Text("HAS-BLED", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        *[state[k] for k in ["sbp160","renal","liver","stroke","bleeding","labile_inr","drugs","alcohol"]],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_has_bled(state)))
    ]

def form_timi(state, on_calc):
    state.clear()
    state["age"] = ft.TextField(label="Edad (años)", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    state["cad_risk_factors"] = ft.Slider(min=0, max=5, divisions=5, label="{value} factores CAD (tabaco, HTA, dislipemia, DM, FH)", value=0)
    for key, lab in [("known_cad","CAD conocida (estenosis ≥50%)"), ("asa_7d","AAS en últimos 7 días"),
                     ("severe_angina","≥2 episodios anginosos en 24 h"), ("st_changes","Cambios ST ≥0.5 mm"),
                     ("positive_markers","Marcadores cardiacos positivos")]:
        state[key] = ft.Switch(label=lab, value=False)
    return [
        ft.Text("TIMI (UA/NSTEMI)", size=20, weight="bold"),
        row_label_control("Edad", state["age"]),
        state["cad_risk_factors"],
        *[state[k] for k in ["known_cad","asa_7d","severe_angina","st_changes","positive_markers"]],
        ft.ElevatedButton("Calcular", on_click=lambda e: on_calc(calc_timi_nstemi(state)))
    ]

def form_heart(state, on_calc):
    state.clear()
    state["history"] = ft.Dropdown(label="Historia", options=[ft.dropdown.Option("slight"), ft.dropdown.Option("moderate"), ft.dropdown.Option("high")], value="moderate", width=220)
    state["ecg"] = ft.Dropdown(label="ECG", options=[ft.dropdown.Option("normal"), ft.dropdown.Option("nonspecific"), ft.dropdown.Option("st_deviation")], value="normal", width=220)
    state["age_band"] = ft.Dropdown(label="Edad", options=[ft.dropdown.Option("lt45"), ft.dropdown.Option("45to64"), ft.dropdown.Option("ge65")], value="45to64", width=160)
    state["riskf"] = ft.Dropdown(label="Factores de riesgo", options=[ft.dropdown.Option("none"), ft.dropdown.Option("one_two"), ft.dropdown.Option("three_or_more")], value="one_two", width=220)
    state["troponin"] = ft.Dropdown(label="Troponina", options=[ft.dropdown.Option("normal"), ft.dropdown.Option("1to3x"), ft.dropdown.Option("gt3x")], value="normal", width=160)
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

# ----------------- App -----------------
def main(page: ft.Page):
    page.title = "Calculadoras cardiovasculares"
    page.padding = 16
    page.theme_mode = "light"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"

    form_state: dict[str, ft.Control] = {}

    result_title = ft.Text("", size=18, weight="bold")
    result_text = ft.Text("", selectable=True)
    result_row = ft.Column(controls=[result_title, result_text], spacing=6)

    def on_calc(res_tuple):
        score, interp = res_tuple
        result_title.value = f"Resultado: {score}"
        result_text.value = interp
        page.update()

    container = ft.Column(spacing=10, width=800)

    def render_form(kind: str):
        help_bar = ft.Row(
            [pill("⚠️ Apoyo clínico"), pill("✅ Datos reales"), pill("🔁 Cambia de score arriba")],
            wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=8
        )
        form_controls = FORMS[kind](form_state, on_calc)
        container.controls = [help_bar, ft.Divider(), *form_controls, ft.Divider(), result_row]
        page.update()

    selector = ft.Dropdown(
        label="Selecciona calculadora",
        options=[ft.dropdown.Option(k) for k in FORMS.keys()],
        width=260
    )

    # Valor inicial seguro
    initial_kind = list(FORMS.keys())[0]
    selector.value = initial_kind
    selector.on_change = lambda e: render_form(selector.value)

    page.add(ft.Text("🫀 Calculadoras de riesgo", size=26, weight="bold"), selector, container)
    render_form(initial_kind)

if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8550))
    )
