import os
import subprocess
import pandas as pd
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random

# Lista de User-Agents para rotar
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

# Variables globales
continuar_ejecucion = True
resultados = []

# INSTALAR NAVEGADORES SI NO EXISTEN
def instalar_navegadores():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudieron instalar los navegadores de Playwright: {e}")
        exit()

# Función para generar URL
def generar_url(base_url, codigo):
    return f"{base_url.rstrip('/')}/{codigo}"

# Función para guardar los resultados en Excel
def guardar_excel():
    global resultados
    if resultados:
        df = pd.DataFrame(resultados)
        archivo_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if archivo_excel:
            df.to_excel(archivo_excel, index=False)
            messagebox.showinfo("Éxito", f"Los datos se han guardado en {archivo_excel}")
    else:
        messagebox.showwarning("Advertencia", "No hay datos para guardar.")

# Función para detener el scraping
def detener_proceso():
    global continuar_ejecucion
    continuar_ejecucion = False
    messagebox.showinfo("Proceso detenido", "El proceso de scraping se ha detenido.")

# Función principal del scraping
def scraping(codigos):
    global continuar_ejecucion, resultados
    resultados = []
    continuar_ejecucion = True

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1920, "height": 1080},
                bypass_csp=True
            )
            page = context.new_page()

            base_url = "https://www.nike.cl/"

            for idx, codigo in enumerate(codigos):
                if not continuar_ejecucion:
                    break

                url_final = generar_url(base_url, codigo)
                progreso.set((idx + 1) / len(codigos) * 100)
                texto_progreso.set(f"Procesando {codigo} ({idx + 1}/{len(codigos)})")
                ventana.update_idletasks()

                try:
                    page.goto(url_final, timeout=60000)

                    nombre_producto = page.inner_text("span.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body")
                    precio_completo = page.inner_text("span.vtex-product-price-1-x-currencyContainer")
                    try:
                        descuento = page.inner_text("span.vtex-product-price-1-x-savingsPercentage")
                    except:
                        descuento = "No aplica"

                    resultados.append({
                        "Código": codigo,
                        "URL": url_final,
                        "Nombre del Producto": nombre_producto,
                        "Precio": precio_completo,
                        "Descuento": descuento
                    })

                    lista.insert(tk.END, f"{codigo} - {nombre_producto}")
                    ventana.update_idletasks()

                except PlaywrightTimeoutError:
                    resultados.append({
                        "Código": codigo,
                        "URL": url_final,
                        "Nombre del Producto": "Error de carga",
                        "Precio": "No disponible",
                        "Descuento": "No disponible"
                    })
                    lista.insert(tk.END, f"{codigo} - Error de carga")
                    ventana.update_idletasks()

            browser.close()
        messagebox.showinfo("Finalizado", "El proceso ha terminado.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para iniciar el scraping en un hilo separado
def iniciar_scraping():
    codigos = entrada_codigos.get("1.0", tk.END).strip().split()
    if codigos:
        threading.Thread(target=scraping, args=(codigos,), daemon=True).start()
    else:
        messagebox.showwarning("Advertencia", "Ingrese al menos un código de producto.")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Scraper Nike - Playwright")
ventana.geometry("600x400")

# Área para pegar códigos
tk.Label(ventana, text="Códigos de producto (separados por espacios):").pack(pady=5)
entrada_codigos = tk.Text(ventana, height=5, width=60)
entrada_codigos.pack(pady=5)

# Botones
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=5)

btn_iniciar = tk.Button(frame_botones, text="Iniciar", command=iniciar_scraping, bg="green", fg="white")
btn_iniciar.pack(side=tk.LEFT, padx=5)

btn_detener = tk.Button(frame_botones, text="Detener", command=detener_proceso, bg="red", fg="white")
btn_detener.pack(side=tk.LEFT, padx=5)

btn_guardar = tk.Button(frame_botones, text="Guardar Excel", command=guardar_excel, bg="blue", fg="white")
btn_guardar.pack(side=tk.LEFT, padx=5)

# Barra de progreso
progreso = tk.DoubleVar()
ttk.Progressbar(ventana, variable=progreso, maximum=100).pack(fill=tk.X, padx=10, pady=5)
texto_progreso = tk.StringVar(value="Esperando...")
tk.Label(ventana, textvariable=texto_progreso).pack()

# Lista de resultados
lista = tk.Listbox(ventana, width=80)
lista.pack(pady=10)

# Instalar navegadores al iniciar
instalar_navegadores()

ventana.mainloop()
