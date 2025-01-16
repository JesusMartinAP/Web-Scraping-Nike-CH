import os
import subprocess
import pandas as pd
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random

# 🌐 Forzar la instalación automática de navegadores
def instalar_navegadores():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al instalar navegadores: {e}")
        exit()

# ✅ Verificar e instalar navegadores
instalar_navegadores()

# Lista de User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
]

# Variables globales
continuar_ejecucion = True
resultados = []

# Función para scraping
def scraping(codigos):
    global continuar_ejecucion, resultados
    resultados = []
    continuar_ejecucion = True

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            for codigo in codigos:
                if not continuar_ejecucion:
                    break
                url = f"https://www.nike.cl/{codigo}"
                page.goto(url, timeout=60000)
                nombre_producto = page.inner_text("h1")
                resultados.append({"Código": codigo, "Nombre": nombre_producto})

            browser.close()
        messagebox.showinfo("Finalizado", "El scraping ha terminado.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# 🖥️ Crear ventana principal
ventana = tk.Tk()
ventana.title("Scraper Nike - Playwright")
ventana.geometry("600x400")

entrada_codigos = tk.Text(ventana, height=5, width=60)
entrada_codigos.pack(pady=5)

def iniciar_scraping():
    codigos = entrada_codigos.get("1.0", tk.END).strip().split()
    threading.Thread(target=scraping, args=(codigos,), daemon=True).start()

btn_iniciar = tk.Button(ventana, text="Iniciar", command=iniciar_scraping, bg="green", fg="white")
btn_iniciar.pack(pady=5)

ventana.mainloop()
