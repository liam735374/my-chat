"""Chat de escritorio con varias conversaciones y opción para compartir por correo."""

import json
import hashlib
import secrets
import random
import re
import tkinter as tk
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, scrolledtext, simpledialog


ARCHIVO_DATOS = Path(__file__).with_name("chats.json")
ARCHIVO_CUENTA = Path(__file__).with_name("cuenta.json")


class AplicacionChat:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Mis chats")
        self.ventana.geometry("900x650")
        self.ventana.minsize(650, 450)
        self.ventana.configure(bg="#f3f5f9")
        if not self.configurar_cuenta():
            self.ventana.destroy()
            return
        self.chats = self.cargar_chats()
        self.chat_actual = next(iter(self.chats), None)
        self.crear_interfaz()
        self.actualizar_lista()
        if self.chat_actual:
            self.mostrar_chat(self.chat_actual)
        else:
            self.nuevo_chat("Mi primer chat")

    def configurar_cuenta(self):
        """Registra la cuenta al principio y muestra inicio de sesión después."""
        cuenta_existente = ARCHIVO_CUENTA.exists()
        try:
            cuenta = json.loads(ARCHIVO_CUENTA.read_text(encoding="utf-8")) if cuenta_existente else None
        except (OSError, json.JSONDecodeError):
            cuenta = None
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Iniciar sesión" if cuenta_existente else "Crear cuenta")
        dialogo.geometry("370x390" if not cuenta_existente else "370x300")
        dialogo.resizable(False, False)
        dialogo.configure(bg="white")
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        dialogo.update_idletasks()
        dialogo.lift()
        dialogo.focus_force()
        tk.Label(dialogo, text="Inicia sesión" if cuenta_existente else "Crea tu cuenta", font=("Segoe UI", 20, "bold"), fg="#202a44", bg="white").pack(pady=(24, 6))
        texto_info = f'Cuenta de {cuenta.get("correo", "")}' if cuenta_existente and cuenta else "Tus datos se guardarán en este dispositivo."
        tk.Label(dialogo, text=texto_info, font=("Segoe UI", 9), fg="#687188", bg="white").pack(pady=(0, 16))

        campos = tk.Frame(dialogo, bg="white")
        campos.pack(fill="x", padx=30)
        entradas = {}
        definiciones = (("Correo electrónico", "correo", False), ("Contraseña", "contrasena", True)) if cuenta_existente else (("Nombre", "nombre", False), ("Correo electrónico", "correo", False), ("Contraseña", "contrasena", True))
        for etiqueta, clave, ocultar in definiciones:
            tk.Label(campos, text=etiqueta, font=("Segoe UI", 9, "bold"), fg="#39445c", bg="white").pack(anchor="w", pady=(7, 3))
            campo = tk.Entry(campos, font=("Segoe UI", 10), relief="solid", bd=1, show="●" if ocultar else "")
            campo.pack(fill="x", ipady=7)
            entradas[clave] = campo

        resultado = {"acceso": False}

        def continuar():
            correo = entradas["correo"].get().strip()
            contrasena = entradas["contrasena"].get()
            if cuenta_existente:
                if not cuenta:
                    messagebox.showerror("No se pudo leer la cuenta", "El archivo de la cuenta está dañado. Elimina cuenta.json para crear una cuenta nueva.", parent=dialogo)
                    return
                clave = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), bytes.fromhex(cuenta["sal"]), 200000).hex()
                if correo.lower() != cuenta["correo"].lower() or not secrets.compare_digest(clave, cuenta["contrasena_hash"]):
                    messagebox.showerror("Datos incorrectos", "El correo o la contraseña no coinciden.", parent=dialogo)
                    return
                resultado["acceso"] = True
                dialogo.destroy()
                return
            nombre = entradas["nombre"].get().strip()
            if not nombre or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
                messagebox.showerror("Revisa tus datos", "Escribe tu nombre y un correo electrónico válido.", parent=dialogo)
                return
            if len(contrasena) < 6:
                messagebox.showerror("Contraseña muy corta", "La contraseña debe tener al menos 6 caracteres.", parent=dialogo)
                return
            sal = secrets.token_hex(16)
            resumen = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), bytes.fromhex(sal), 200000).hex()
            ARCHIVO_CUENTA.write_text(json.dumps({"nombre": nombre, "correo": correo, "sal": sal, "contrasena_hash": resumen}, ensure_ascii=False, indent=2), encoding="utf-8")
            resultado["acceso"] = True
            dialogo.destroy()

        texto_boton = "Iniciar sesión" if cuenta_existente else "Crear cuenta"
        tk.Button(dialogo, text=texto_boton, command=continuar, font=("Segoe UI", 10, "bold"), bg="#3857d6", fg="white", relief="flat", padx=18, pady=9, cursor="hand2").pack(pady=20)
        dialogo.protocol("WM_DELETE_WINDOW", dialogo.destroy)
        self.ventana.wait_window(dialogo)
        return resultado["acceso"]

    def cargar_chats(self):
        try:
            datos = json.loads(ARCHIVO_DATOS.read_text(encoding="utf-8"))
            return datos if isinstance(datos, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def guardar_chats(self):
        ARCHIVO_DATOS.write_text(json.dumps(self.chats, ensure_ascii=False, indent=2), encoding="utf-8")

    def crear_interfaz(self):
        lateral = tk.Frame(self.ventana, bg="#202a44", width=230)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="Mis chats", font=("Segoe UI", 17, "bold"), fg="white", bg="#202a44").pack(anchor="w", padx=18, pady=(20, 14))
        tk.Button(lateral, text="＋  Nuevo chat", command=self.pedir_chat, font=("Segoe UI", 10, "bold"), bg="#526de0", fg="white", relief="flat", padx=10, pady=9, cursor="hand2").pack(fill="x", padx=12, pady=(0, 12))
        self.lista = tk.Listbox(lateral, bg="#202a44", fg="#e8ecf8", selectbackground="#526de0", selectforeground="white", font=("Segoe UI", 10), relief="flat", borderwidth=0, activestyle="none", highlightthickness=0)
        self.lista.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        self.lista.bind("<<ListboxSelect>>", self.seleccionar_chat)

        principal = tk.Frame(self.ventana, bg="#f3f5f9")
        principal.pack(side="left", fill="both", expand=True)
        encabezado = tk.Frame(principal, bg="#3857d6", padx=20, pady=14)
        encabezado.pack(fill="x")
        self.titulo = tk.Label(encabezado, text="Chat", font=("Segoe UI", 18, "bold"), fg="white", bg="#3857d6")
        self.titulo.pack(side="left")
        tk.Button(encabezado, text="Compartir por correo", command=self.compartir_correo, font=("Segoe UI", 9, "bold"), bg="white", fg="#3857d6", relief="flat", padx=12, pady=7, cursor="hand2").pack(side="right")

        self.historial = scrolledtext.ScrolledText(principal, wrap=tk.WORD, state="disabled", font=("Segoe UI", 11), bg="white", fg="#202638", padx=14, pady=14, relief="flat", borderwidth=0)
        self.historial.pack(fill="both", expand=True, padx=16, pady=(16, 10))
        self.historial.tag_config("usuario", foreground="#3857d6", font=("Segoe UI", 10, "bold"))
        self.historial.tag_config("asistente", foreground="#21805a", font=("Segoe UI", 10, "bold"))
        self.historial.tag_config("hora", foreground="#8991a3", font=("Segoe UI", 8))
        self.historial.tag_config("mensaje", foreground="#202638", font=("Segoe UI", 11))

        barra = tk.Frame(principal, bg="#f3f5f9", padx=16, pady=0)
        barra.pack(fill="x")
        self.entrada = tk.Entry(barra, font=("Segoe UI", 11), relief="solid", bd=1, highlightthickness=1, highlightbackground="#dce1eb", highlightcolor="#3857d6")
        self.entrada.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self.entrada.bind("<Return>", self.enviar)
        tk.Button(barra, text="Enviar", command=self.enviar, font=("Segoe UI", 10, "bold"), bg="#3857d6", fg="white", activebackground="#2d47b8", relief="flat", padx=18, pady=10, cursor="hand2").pack(side="right")

    def actualizar_lista(self):
        self.lista.delete(0, "end")
        for nombre in self.chats:
            self.lista.insert("end", nombre)
        if self.chat_actual in self.chats:
            indice = list(self.chats).index(self.chat_actual)
            self.lista.selection_set(indice)
            self.lista.activate(indice)

    def pedir_chat(self):
        nombre = simpledialog.askstring("Nuevo chat", "¿Qué nombre quieres darle al chat?", parent=self.ventana)
        if nombre and nombre.strip():
            self.nuevo_chat(nombre.strip())

    def nuevo_chat(self, nombre):
        base, numero = nombre, 2
        while nombre in self.chats:
            nombre = f"{base} ({numero})"
            numero += 1
        self.chats[nombre] = [{"autor": "Chat", "texto": "¡Hola! Soy un chatbot sencillo. Escribe algo para empezar.", "hora": datetime.now().strftime("%H:%M")}]
        self.chat_actual = nombre
        self.guardar_chats()
        self.actualizar_lista()
        self.mostrar_chat(nombre)

    def seleccionar_chat(self, _evento=None):
        seleccion = self.lista.curselection()
        if seleccion:
            nombre = self.lista.get(seleccion[0])
            if nombre != self.chat_actual:
                self.chat_actual = nombre
                self.mostrar_chat(nombre)

    def mostrar_chat(self, nombre):
        self.titulo.config(text=nombre)
        self.historial.configure(state="normal")
        self.historial.delete("1.0", "end")
        for mensaje in self.chats[nombre]:
            etiqueta = "usuario" if mensaje["autor"] == "Tú" else "asistente"
            self.historial.insert("end", f'{mensaje["autor"]}  ', etiqueta)
            self.historial.insert("end", f'{mensaje["hora"]}\n', "hora")
            self.historial.insert("end", f'{mensaje["texto"]}\n\n', "mensaje")
        self.historial.configure(state="disabled")
        self.historial.see("end")

    def agregar_mensaje(self, autor, texto):
        mensaje = {"autor": autor, "texto": texto, "hora": datetime.now().strftime("%H:%M")}
        self.chats[self.chat_actual].append(mensaje)
        self.guardar_chats()
        self.historial.configure(state="normal")
        etiqueta = "usuario" if autor == "Tú" else "asistente"
        self.historial.insert("end", f'{autor}  ', etiqueta)
        self.historial.insert("end", f'{mensaje["hora"]}\n', "hora")
        self.historial.insert("end", f'{texto}\n\n', "mensaje")
        self.historial.configure(state="disabled")
        self.historial.see("end")

    def enviar(self, _evento=None):
        texto = self.entrada.get().strip()
        if texto:
            self.entrada.delete(0, "end")
            self.agregar_mensaje("Tú", texto)
            respuesta = self.responder(texto)
            chat = self.chat_actual
            self.ventana.after(250, lambda: self.agregar_mensaje("Chat", respuesta) if chat == self.chat_actual else self.agregar_a_chat(chat, "Chat", respuesta))

    def agregar_a_chat(self, nombre, autor, texto):
        self.chats[nombre].append({"autor": autor, "texto": texto, "hora": datetime.now().strftime("%H:%M")})
        self.guardar_chats()

    def compartir_correo(self):
        mensajes = self.chats.get(self.chat_actual, [])
        cuerpo = "\n".join(f'{m["autor"]} ({m["hora"]}): {m["texto"]}' for m in mensajes)
        url = "mailto:?" + urllib.parse.urlencode({"subject": f"Conversación: {self.chat_actual}", "body": cuerpo})
        try:
            if len(url) > 8000:
                messagebox.showwarning("Conversación extensa", "El chat es demasiado largo para incluirlo en un correo. Puedes copiar un fragmento y enviarlo manualmente.")
            elif not webbrowser.open(url):
                messagebox.showerror("No se pudo abrir el correo", "Configura una aplicación de correo predeterminada e inténtalo de nuevo.")
        except Exception as error:
            messagebox.showerror("No se pudo abrir el correo", f"Revisa que tengas una aplicación de correo configurada.\n\n{error}")

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
            return random.choice(("¿Qué hace una abeja en el gimnasio? ¡Zum-ba!", "¿Por qué el libro de matemáticas estaba triste? Porque tenía muchos problemas.", "¿Qué le dice un techo a otro? Techo de menos."))
        if re.search(r"\b(gracias|muchas gracias)\b", mensaje):
            return "¡De nada! Aquí estoy si quieres seguir charlando."
        if re.search(r"\b(adiós|adios|hasta luego|chau|chao)\b", mensaje):
            return "¡Hasta luego! Que tengas un buen día."
        if "cómo estás" in mensaje or "como estas" in mensaje:
            return "¡Estoy muy bien y listo para conversar! ¿Y tú?"
        return random.choice(("¡Qué interesante! Cuéntame un poco más.", "Entiendo. ¿Qué más te gustaría comentar?", "Gracias por contármelo. ¿Cómo te hace sentir eso?", "Todavía estoy aprendiendo, pero me gusta conversar contigo."))


if __name__ == "__main__":
    ventana = tk.Tk()
    AplicacionChat(ventana)
    ventana.mainloop()
