#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Automatización de Git - Versión Ultra Simplificada
Hace todo automáticamente con un solo clic
"""

import os
import subprocess
import json
import sys
from datetime import datetime
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog

CONFIG_FILE = "git_config.json"


def ejecutar_comando(comando):
    """Ejecuta un comando y retorna el resultado"""
    try:
        resultado = subprocess.run(
            comando, shell=True, capture_output=True, text=True,
            encoding='utf-8', errors='ignore'
        )
        salida = resultado.stdout.strip() if resultado.stdout else ""
        error = resultado.stderr.strip() if resultado.stderr else ""
        return resultado.returncode == 0, salida, error
    except:
        return False, "", ""


def configurar_git_automatico():
    """Configura Git automáticamente si no está configurado"""
    # Verificar si ya está configurado
    exito, nombre, _ = ejecutar_comando("git config user.name")
    exito2, email, _ = ejecutar_comando("git config user.email")
    
    if not exito or not nombre.strip():
        # Configurar nombre automáticamente
        ejecutar_comando('git config --global user.name "Usuario Git"')
    
    if not exito2 or not email.strip():
        # Configurar email automáticamente
        ejecutar_comando('git config --global user.email "usuario@git.local"')
    
    return True


def es_primera_vez():
    """Verifica si es la primera vez"""
    if not os.path.exists(".git") or not os.path.exists(CONFIG_FILE):
        return True
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return not json.load(f).get('configurado', False)
    except:
        return True


def guardar_configuracion(config):
    """Guarda la configuración"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False


def cargar_configuracion():
    """Carga la configuración"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


class GitAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Git Automático")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variables
        self.url_remoto = StringVar()
        self.ruta_proyecto = StringVar()
        self.directorio_actual = os.getcwd()
        self.ruta_proyecto_usuario = None
        
        self.crear_interfaz()
        
        # SIEMPRE pedir la carpeta del proyecto del usuario al iniciar
        self.seleccionar_carpeta_proyecto_inicio()
    
    def crear_interfaz(self):
        """Crea la interfaz"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title = Label(
            main_frame,
            text="🚀 Automatización de Git",
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=(0, 20))
        
        # Área de salida
        self.output = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=60,
            wrap=WORD,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#4caf50",
            state=DISABLED
        )
        self.output.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Frame de botones
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack()
    
    def log(self, mensaje, tipo="info"):
        """Agrega mensaje"""
        self.output.config(state=NORMAL)
        iconos = {"info": "ℹ", "success": "✓", "error": "✗", "warning": "⚠"}
        self.output.insert(END, f"{iconos.get(tipo, '')} {mensaje}\n")
        self.output.config(state=DISABLED)
        self.output.see(END)
        self.root.update()
    
    def seleccionar_carpeta_proyecto_inicio(self):
        """Al iniciar, siempre pregunta por la carpeta del proyecto del usuario"""
        self.log("👋 ¡Bienvenido al Sistema de Automatización de Git!", "info")
        self.log("\n📋 INSTRUCCIONES:", "info")
        self.log("Este programa te ayuda a guardar y subir tus cambios a GitHub", "info")
        self.log("de forma automática, sin escribir comandos complicados.", "info")
        
        # Limpiar botones
        for w in self.btn_frame.winfo_children():
            w.destroy()
        
        # Frame principal de selección
        main_select_frame = ttk.LabelFrame(self.btn_frame, text="📁 PASO 1: Selecciona la carpeta de TU PROYECTO", padding="15")
        main_select_frame.pack(pady=15, fill=X)
        
        Label(
            main_select_frame,
            text="💡 IMPORTANTE: Selecciona la carpeta donde está TU PROYECTO",
            font=("Arial", 10, "bold"),
            fg="#d32f2f"
        ).pack(anchor=W, pady=(0, 10))
        
        Label(
            main_select_frame,
            text="Ejemplo: Si tu proyecto está en 'C:\\MisProyectos\\MiApp',\nselecciona esa carpeta (no la carpeta de este programa)",
            font=("Arial", 9),
            fg="#666",
            justify=LEFT
        ).pack(anchor=W, pady=(0, 15))
        
        # Frame para ruta y botón
        ruta_frame = Frame(main_select_frame)
        ruta_frame.pack(fill=X, pady=5)
        
        ttk.Label(ruta_frame, text="Ruta de tu proyecto:", font=("Arial", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        ruta_entry = ttk.Entry(ruta_frame, textvariable=self.ruta_proyecto, width=55, font=("Consolas", 9))
        ruta_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        btn_seleccionar = Button(
            ruta_frame,
            text="📂 Navegar y Seleccionar...",
            command=self.buscar_carpeta,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_seleccionar.pack(side=LEFT)
        
        # Si es primera vez, mostrar configuración de GitHub
        if es_primera_vez():
            # Frame de URL
            url_frame = ttk.LabelFrame(self.btn_frame, text="🔗 PASO 2: Conectar con GitHub (Opcional)", padding="15")
            url_frame.pack(pady=10, fill=X)
            
            Label(
                url_frame,
                text="💡 ¿Qué es esto? Conecta tu proyecto con GitHub para guardar tus cambios en internet",
                font=("Arial", 9, "italic"),
                fg="#666",
                justify=LEFT
            ).pack(anchor=W, pady=(0, 10))
            
            instrucciones_text = (
                "📋 Cómo obtener la URL:\n"
                "   1. Ve a tu repositorio en GitHub\n"
                "   2. Haz clic en el botón verde 'Code' (arriba a la derecha)\n"
                "   3. Selecciona la pestaña 'HTTPS'\n"
                "   4. Copia la URL que aparece\n"
                "\n"
                "📌 Ejemplo: https://github.com/Grato390/git-automatizado.git"
            )
            
            Label(
                url_frame,
                text=instrucciones_text,
                font=("Arial", 8),
                fg="#555",
                justify=LEFT
            ).pack(anchor=W, pady=(0, 10))
            
            ttk.Label(url_frame, text="Pega la URL aquí (opcional):", font=("Arial", 10, "bold")).pack(anchor=W, pady=(0, 5))
            
            url_entry = ttk.Entry(url_frame, textvariable=self.url_remoto, width=55, font=("Consolas", 10))
            url_entry.pack(fill=X, pady=5)
            url_entry.insert(0, "https://github.com/usuario/repositorio.git")
            url_entry.bind("<FocusIn>", lambda e: url_entry.delete(0, END) if url_entry.get() == "https://github.com/usuario/repositorio.git" else None)
            
            # Botón principal
            btn_auto = Button(
                self.btn_frame,
                text="🚀 CONFIGURAR Y CONTINUAR",
                command=self.hacer_todo_automatico,
                bg="#4caf50",
                fg="white",
                font=("Arial", 12, "bold"),
                padx=20,
                pady=12,
                cursor="hand2"
            )
            btn_auto.pack(pady=15)
        else:
            # Si ya está configurado, solo necesita seleccionar carpeta
            btn_continuar = Button(
                self.btn_frame,
                text="✅ CONTINUAR CON ESTA CARPETA",
                command=self.continuar_con_carpeta,
                bg="#4caf50",
                fg="white",
                font=("Arial", 11, "bold"),
                padx=20,
                pady=10,
                cursor="hand2"
            )
            btn_continuar.pack(pady=15)
            
            # Enter en el entry también continúa
            ruta_entry.bind("<Return>", lambda e: self.continuar_con_carpeta())
    
    def continuar_con_carpeta(self):
        """Continúa con la carpeta seleccionada"""
        ruta = self.ruta_proyecto.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto")
            return
        
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "La carpeta seleccionada no existe")
            return
        
        self.ruta_proyecto_usuario = ruta
        os.chdir(ruta)
        self.log(f"\n✓ Carpeta seleccionada: {ruta}", "success")
        self.mostrar_interfaz_principal()
    
    def buscar_carpeta(self):
        """Abre diálogo para seleccionar carpeta"""
        carpeta = filedialog.askdirectory(
            title="Selecciona la carpeta de TU PROYECTO",
            initialdir=os.path.expanduser("~")
        )
        if carpeta:
            self.ruta_proyecto.set(carpeta)
            self.log(f"✓ Carpeta seleccionada: {carpeta}", "success")
    
    def actualizar_automatico(self):
        """Actualiza todo automáticamente con explicaciones paso a paso"""
        # Verificar que hay una carpeta seleccionada
        if not self.ruta_proyecto_usuario:
            ruta = self.ruta_proyecto.get().strip()
            if not ruta or not os.path.exists(ruta):
                messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto primero")
                self.seleccionar_carpeta_proyecto_inicio()
                return
            self.ruta_proyecto_usuario = ruta
        
        # Cambiar al directorio del proyecto del usuario
        os.chdir(self.ruta_proyecto_usuario)
    
    def hacer_todo_automatico(self):
        """Hace TODO automáticamente con explicaciones"""
        # 1. Cambiar al directorio del proyecto
        ruta = self.ruta_proyecto.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto")
            return
        
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "La carpeta seleccionada no existe")
            return
        
        self.log("\n" + "="*60, "info")
        self.log("🚀 CONFIGURACIÓN INICIAL DEL PROYECTO", "info")
        self.log("="*60, "info")
        self.log(f"\n📁 Carpeta del proyecto: {ruta}", "info")
        self.log("   Cambiando a esta carpeta...", "info")
        os.chdir(ruta)
        
        # Verificar Git
        self.log("\n🔍 Verificando si Git está instalado...", "info")
        exito, _, _ = ejecutar_comando("git --version")
        if not exito:
            self.log("   ✗ Git no está instalado", "error")
            messagebox.showerror("Error", "Git no está instalado.\n\nInstálalo desde: https://git-scm.com/downloads")
            return
        self.log("   ✓ Git está instalado", "success")
        
        # 2. Inicializar Git
        self.log("\n📦 PASO 1: Inicializando el sistema de control de versiones...", "info")
        self.log("   ¿Qué hace esto? Prepara tu carpeta para usar Git", "info")
        self.log("   Comando: git init", "info")
        
        if not os.path.exists(".git"):
            exito, _, _ = ejecutar_comando("git init")
            if exito:
                self.log("   ✓ ¡Sistema inicializado correctamente!", "success")
            else:
                self.log("   ✗ Error al inicializar", "error")
                return
        else:
            self.log("   ✓ El sistema ya estaba inicializado", "success")
        
        # 3. Configurar remoto
        url = self.url_remoto.get().strip()
        if url and url != "https://github.com/usuario/repositorio.git":
            self.log("\n🔗 PASO 2: Conectando con GitHub...", "info")
            self.log("   ¿Qué hace esto? Conecta tu proyecto local con GitHub", "info")
            self.log(f"   URL: {url}", "info")
            self.log("   Comando: git remote add origin \"URL\"", "info")
            
            ejecutar_comando(f'git remote add origin "{url}"')
            ejecutar_comando(f'git remote set-url origin "{url}"')
            self.log("   ✓ ¡Conectado con GitHub correctamente!", "success")
        else:
            url = None
            self.log("\n⚠ No se configuró conexión con GitHub", "warning")
            self.log("   (Puedes agregarlo después si lo necesitas)", "info")
        
        # Guardar configuración
        guardar_configuracion({
            'configurado': True,
            'url_remoto': url,
            'ruta_proyecto': ruta
        })
        
        self.log("\n" + "="*60, "success")
        self.log("✅ ¡CONFIGURACIÓN COMPLETADA!", "success")
        self.log("="*60, "success")
        self.log("\n📊 RESUMEN:", "info")
        self.log("   ✓ Sistema Git inicializado", "success")
        if url:
            self.log("   ✓ Conectado con GitHub", "success")
        self.log("\n🎉 ¡Ahora puedes usar los botones para actualizar tu proyecto!", "success")
        
        messagebox.showinfo("Éxito", "¡Todo configurado correctamente!\n\nAhora puedes usar los botones para:\n• Agregar cambios\n• Guardar cambios\n• Subir a GitHub")
        
        # Mostrar interfaz principal
        self.mostrar_interfaz_principal()
    
    def mostrar_interfaz_principal(self):
        """Interfaz principal simplificada"""
        # Limpiar
        for w in self.btn_frame.winfo_children():
            w.destroy()
        
        # Mostrar información del proyecto actual
        ruta_actual = self.ruta_proyecto_usuario or os.getcwd()
        self.log(f"\n📁 Proyecto actual: {ruta_actual}", "success")
        
        config = cargar_configuracion()
        if config.get('url_remoto'):
            self.log(f"🔗 Conectado a: {config['url_remoto']}", "success")
        else:
            self.log("⚠ Sin conexión a GitHub (puedes trabajar localmente)", "warning")
        
        # Frame de información
        info_frame = Frame(self.btn_frame, bg="#e3f2fd", relief=SOLID, borderwidth=1)
        info_frame.pack(pady=(0, 15), fill=X)
        
        info_text = (
            "💡 ¿Qué hace cada botón?\n"
            "• Botón AZUL: Agrega, guarda y sube todos tus cambios\n"
            "• Botón NARANJA: Solo prepara tus archivos (no los guarda todavía)"
        )
        
        Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            bg="#e3f2fd",
            fg="#1976d2",
            justify=LEFT
        ).pack(padx=10, pady=8, anchor=W)
        
        # UN SOLO BOTÓN PRINCIPAL - hace todo
        btn_principal = Button(
            self.btn_frame,
            text="🔄 ACTUALIZAR TODO\n(Agregar + Guardar + Subir)",
            command=self.actualizar_automatico,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=12,
            cursor="hand2",
            justify=CENTER
        )
        btn_principal.pack(pady=10)
        
        # Botón secundario para solo agregar
        btn_add = Button(
            self.btn_frame,
            text="➕ Solo Preparar Archivos\n(No guarda, solo los marca)",
            command=self.solo_agregar,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=8,
            cursor="hand2",
            justify=CENTER
        )
        btn_add.pack(pady=5)
    
    
    def actualizar_automatico(self):
        """Actualiza todo automáticamente - SIMPLIFICADO"""
        # Verificar que hay una carpeta seleccionada
        if not self.ruta_proyecto_usuario:
            ruta = self.ruta_proyecto.get().strip()
            if not ruta or not os.path.exists(ruta):
                messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto primero")
                self.seleccionar_carpeta_proyecto_inicio()
                return
            self.ruta_proyecto_usuario = ruta
        
        # Cambiar al directorio del proyecto del usuario
        os.chdir(self.ruta_proyecto_usuario)
        self.log(f"\n📁 Trabajando en: {self.ruta_proyecto_usuario}", "info")
        
        # Configurar Git automáticamente si no está configurado
        self.log("🔧 Configurando Git automáticamente...", "info")
        configurar_git_automatico()
        self.log("✓ Git configurado", "success")
        
        self.log("\n" + "="*60, "info")
        self.log("🚀 INICIANDO ACTUALIZACIÓN AUTOMÁTICA", "info")
        self.log("="*60, "info")
        
        # PASO 1: Agregar TODOS los archivos
        self.log("\n📋 PASO 1: Agregando todos los archivos...", "info")
        self.log("   Comando: git add .", "info")
        ejecutar_comando("git add .")
        
        # Verificar si hay cambios
        exito, salida, _ = ejecutar_comando("git status --porcelain")
        if not salida.strip():
            self.log("   ⚠ No hay cambios nuevos", "warning")
            return
        
        self.log("   ✓ Archivos agregados", "success")
        self.log(f"   📁 {len(salida.strip().split(chr(10)))} archivo(s) preparado(s)", "info")
        
        # PASO 2: Commit automático con mensaje por defecto
        from datetime import datetime
        mensaje = f"Actualización automática - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.log("\n💾 PASO 2: Guardando cambios...", "info")
        self.log(f"   Mensaje: {mensaje}", "info")
        self.log("   Comando: git commit -m \"mensaje\"", "info")
        
        exito, _, error = ejecutar_comando(f'git commit -m "{mensaje}"')
        if exito:
            self.log("   ✓ Cambios guardados", "success")
        else:
            self.log(f"   ✗ Error: {error}", "error")
            return
        
        # PASO 3: Preguntar si hacer push
        config = cargar_configuracion()
        if config.get('url_remoto'):
            respuesta = messagebox.askyesno(
                "¿Subir a GitHub?",
                f"¿Deseas subir los cambios a GitHub?\n\nRepositorio: {config['url_remoto']}"
            )
            
            if respuesta:
                self.log("\n☁️ PASO 3: Subiendo a GitHub...", "info")
                self.log("   Comando: git push origin main", "info")
                
                exito, _, _ = ejecutar_comando("git push origin main")
                if not exito:
                    exito, _, _ = ejecutar_comando("git push origin master")
                if exito:
                    self.log("   ✓ Cambios subidos a GitHub", "success")
                else:
                    self.log("   ⚠ No se pudo subir", "warning")
            else:
                self.log("\n⚠ Push cancelado por el usuario", "warning")
        else:
            self.log("\n⚠ No hay repositorio configurado", "warning")
        
        self.log("\n" + "="*60, "success")
        self.log("✅ ¡COMPLETADO!", "success")
        self.log("="*60, "success")
    
    def solo_agregar(self):
        """Solo agrega cambios sin commit/push"""
        # Verificar que hay una carpeta seleccionada
        if not self.ruta_proyecto_usuario:
            ruta = self.ruta_proyecto.get().strip()
            if not ruta or not os.path.exists(ruta):
                messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto primero")
                self.seleccionar_carpeta_proyecto_inicio()
                return
            self.ruta_proyecto_usuario = ruta
        
        os.chdir(self.ruta_proyecto_usuario)
        
        self.log("\n" + "="*60, "info")
        self.log("➕ AGREGANDO CAMBIOS (Solo preparar archivos)", "info")
        self.log("="*60, "info")
        self.log("\n📋 ¿Qué hace esto?", "info")
        self.log("   Marca tus archivos modificados para guardarlos después", "info")
        self.log("   Comando: git add .", "info")
        self.log("   (No los guarda todavía, solo los prepara)", "info")
        
        ejecutar_comando("git add .")
        
        exito, salida, _ = ejecutar_comando("git status --porcelain")
        if salida.strip():
            self.log(f"\n   ✓ ¡Archivos preparados! ({len(salida.strip().split(chr(10)))} archivo(s))", "success")
            self.log("\n💡 Siguiente paso: Usa el botón 'ACTUALIZAR TODO' para guardar y subir", "info")
        else:
            self.log("\n   ⚠ No hay cambios para agregar", "warning")
        
        self.log("\n" + "="*60, "info")


def main():
    root = Tk()
    app = GitAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
