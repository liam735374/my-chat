"""Chat de escritorio sencillo en español, hecho con la biblioteca estándar."""

import random
import re
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext


class AplicacionChat:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Mi chat")
        self.ventana.geometry("620x680")
        self.ventana.minsize(420, 480)
        self.ventana.configure(bg="#f3f5f9")

        encabezado = tk.Frame(ventana, bg="#3857d6", padx=20, pady=16)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text="Mi chat",
            font=("Segoe UI", 19, "bold"),
            fg="white",
            bg="#3857d6",
        ).pack(anchor="w")
        tk.Label(
            encabezado,
            text="Una conversación sencilla, directamente en tu computadora",
            font=("Segoe UI", 9),
            fg="#e1e7ff",
            bg="#3857d6",
        ).pack(anchor="w", pady=(3, 0))

        self.historial = scrolledtext.ScrolledText(
            ventana,
            wrap=tk.WORD,
            state="disabled",
            font=("Segoe UI", 11),
            bg="white",
            fg="#202638",
            padx=14,
            pady=14,
            relief="flat",
            borderwidth=0,
            spacing1=4,
            spacing3=8,
        )
        self.historial.pack(fill="both", expand=True, padx=16, pady=(16, 10))
        self.historial.tag_config("usuario", foreground="#3857d6", font=("Segoe UI", 10, "bold"))
        self.historial.tag_config("asistente", foreground="#21805a", font=("Segoe UI", 10, "bold"))
        self.historial.tag_config("hora", foreground="#8991a3", font=("Segoe UI", 8))
        self.historial.tag_config("mensaje", foreground="#202638", font=("Segoe UI", 11))

        sugerencias = tk.Frame(ventana, bg="#f3f5f9")
        sugerencias.pack(fill="x", padx=16, pady=(0, 8))
        for texto in ("¿Qué puedes hacer?", "Cuéntame un chiste"):
            tk.Button(
                sugerencias,
                text=texto,
                command=lambda t=texto: self.enviar_texto(t),
                font=("Segoe UI", 9),
                bg="white",
                fg="#49536a",
                activebackground="#e8ecf8",
                relief="flat",
                padx=10,
                pady=6,
                cursor="hand2",
            ).pack(side="left", padx=(0, 8))

        barra = tk.Frame(ventana, bg="#f3f5f9", padx=16, pady=0)
        barra.pack(fill="x")
        self.entrada = tk.Entry(
            barra,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#dce1eb",
            highlightcolor="#3857d6",
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self.entrada.bind("<Return>", self.enviar)
        tk.Button(
            barra,
            text="Enviar",
            command=self.enviar,
            font=("Segoe UI", 10, "bold"),
            bg="#3857d6",
            fg="white",
            activebackground="#2d47b8",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(side="right")

        self.agregar_mensaje("Chat", "¡Hola! Soy un chatbot sencillo. Escribe algo para empezar.")
        self.entrada.focus_set()

    def agregar_mensaje(self, autor, texto):
        hora = datetime.now().strftime("%H:%M")
        etiqueta = "usuario" if autor == "Tú" else "asistente"
        self.historial.configure(state="normal")
        self.historial.insert("end", f"{autor}  ", etiqueta)
        self.historial.insert("end", f"{hora}\n", "hora")
        self.historial.insert("end", f"{texto}\n\n", "mensaje")
        self.historial.configure(state="disabled")
        self.historial.see("end")

    def enviar(self, _evento=None):
        texto = self.entrada.get().strip()
        if texto:
            self.enviar_texto(texto)

    def enviar_texto(self, texto):
        self.entrada.delete(0, "end")
        self.agregar_mensaje("Tú", texto)
        respuesta = self.responder(texto)
        self.ventana.after(250, lambda: self.agregar_mensaje("Chat", respuesta))

    @staticmethod
    def responder(texto):
        mensaje = texto.lower().strip()
        if re.search(r"\b(hola|buenas|buenos días|buenas tardes|buenas noches)\b", mensaje):
            return random.choice(("¡Hola! ¿Cómo va tu día?", "¡Buenas! Me alegra conversar contigo."))
        if "qué puedes hacer" in mensaje or "que puedes hacer" in mensaje or "ayuda" in mensaje:
            return "Puedo saludarte, conversar un poco, decirte la hora o contarte un chiste. ¡Prueba escribiendo!"
        if "hora" in mensaje:
            return f"Ahora son las {datetime.now().strftime('%H:%M')}."
        if "chiste" in mensaje:
            return random.choice((
                "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
                "¿Por qué el libro de matemáticas estaba triste? Porque tenía muchos problemas.",
                "¿Qué le dice un techo a otro? Techo de menos.",
            ))
        if re.search(r"\b(gracias|muchas gracias)\b", mensaje):
            return "¡De nada! Aquí estoy si quieres seguir charlando."
        if re.search(r"\b(adiós|adios|hasta luego|chau|chao)\b", mensaje):
            return "¡Hasta luego! Que tengas un buen día."
        if "cómo estás" in mensaje or "como estas" in mensaje:
            return "¡Estoy muy bien y listo para conversar! ¿Y tú?"
        return random.choice((
            "¡Qué interesante! Cuéntame un poco más.",
            "Entiendo. ¿Qué más te gustaría comentar?",
            "Gracias por contármelo. ¿Cómo te hace sentir eso?",
            "Todavía estoy aprendiendo, pero me gusta conversar contigo.",
        ))


if __name__ == "__main__":
    ventana = tk.Tk()
    AplicacionChat(ventana)
    ventana.mainloop()
