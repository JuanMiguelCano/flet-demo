import flet as ft
import os

def main(page: ft.Page):
    page.title = "Demo Flet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    title = ft.Text("¡Hola Flet en Ubuntu! 🐧", size=28, weight="bold")
    counter = ft.Text("Has hecho 0 clics", size=18)
    clicks = 0

    name = ft.TextField(label="Tu nombre", hint_text="Escríbelo aquí...", width=300)
    toast = ft.SnackBar(content=ft.Text("¡Guardado!"), open=False)

    def on_click(e):
        nonlocal clicks
        clicks += 1
        counter.value = f"Has hecho {clicks} clics"
        page.update()

    def on_save(e):
        toast.content = ft.Text(f"Hola {name.value or 'anónimo'} 👋")
        toast.open = True
        page.update()

    page.snack_bar = toast

    page.add(
        title,
        counter,
        ft.Row(
            [
                ft.ElevatedButton("Sumar clic", on_click=on_click),
                ft.OutlinedButton("Guardar nombre", on_click=on_save),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        name,
    )

if __name__ == "__main__":
    # Render (y otros hostings) usan la variable de entorno PORT
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8550))
    )