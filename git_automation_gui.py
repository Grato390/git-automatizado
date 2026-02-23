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
import threading
from datetime import datetime
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Para Windows: ocultar ventana de consola
if sys.platform == 'win32':
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUPINFO.wShowWindow = subprocess.SW_HIDE
else:
    STARTUPINFO = None

CONFIG_FILE = "git_config.json"
HISTORIAL_FILE = "historial_proyectos.txt"
PROYECTOS_FILE = "proyectos_guardados.json"


def ejecutar_comando(comando):
    """Ejecuta un comando en segundo plano sin mostrar ventana de consola"""
    try:
        resultado = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8', 
            errors='ignore',
            startupinfo=STARTUPINFO,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
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


def guardar_proyecto(ruta, url_remoto=None):
    """Guarda un proyecto en el historial con seguridad"""
    try:
        # Cargar proyectos existentes
        proyectos = {}
        if os.path.exists(PROYECTOS_FILE):
            try:
                with open(PROYECTOS_FILE, 'r', encoding='utf-8') as f:
                    proyectos = json.load(f)
            except:
                proyectos = {}
        
        # Validar que la ruta existe (seguridad)
        if not os.path.exists(ruta):
            return False
        
        # Normalizar ruta para evitar duplicados
        ruta_normalizada = os.path.normpath(ruta)
        
        # Guardar proyecto
        proyectos[ruta_normalizada] = {
            'ruta': ruta_normalizada,
            'url_remoto': url_remoto,
            'fecha_ultimo_acceso': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_creacion': proyectos.get(ruta_normalizada, {}).get('fecha_creacion', 
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        
        # Guardar en JSON (estructurado)
        with open(PROYECTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(proyectos, f, indent=4, ensure_ascii=False)
        
        # Guardar en TXT (historial legible)
        with open(HISTORIAL_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Proyecto: {ruta_normalizada}\n")
            if url_remoto:
                f.write(f"  Remoto: {url_remoto}\n")
            f.write("\n")
        
        return True
    except Exception as e:
        return False


def cargar_proyectos():
    """Carga todos los proyectos guardados"""
    if not os.path.exists(PROYECTOS_FILE):
        return {}
    try:
        with open(PROYECTOS_FILE, 'r', encoding='utf-8') as f:
            proyectos = json.load(f)
            # Validar que las rutas aún existen (seguridad)
            proyectos_validos = {}
            for ruta, datos in proyectos.items():
                if os.path.exists(ruta):
                    proyectos_validos[ruta] = datos
            return proyectos_validos
    except:
        return {}


def obtener_ultimo_proyecto():
    """Obtiene el último proyecto usado"""
    proyectos = cargar_proyectos()
    if not proyectos:
        return None
    
    # Ordenar por fecha de último acceso
    proyectos_ordenados = sorted(
        proyectos.items(),
        key=lambda x: x[1].get('fecha_ultimo_acceso', ''),
        reverse=True
    )
    
    if proyectos_ordenados:
        return proyectos_ordenados[0][1]  # Retorna datos del más reciente
    return None


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
        
        # Intentar cargar último proyecto usado
        ultimo_proyecto = obtener_ultimo_proyecto()
        if ultimo_proyecto:
            self.ruta_proyecto_usuario = ultimo_proyecto['ruta']
            self.ruta_proyecto.set(ultimo_proyecto['ruta'])
            if ultimo_proyecto.get('url_remoto'):
                self.url_remoto.set(ultimo_proyecto['url_remoto'])
            self.log(f"✓ Proyecto cargado: {ultimo_proyecto['ruta']}", "success")
            self.mostrar_interfaz_principal()
        else:
            # Si no hay proyecto guardado, pedir selección
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
        
        # Verificar si hay proyectos guardados
        proyectos = cargar_proyectos()
        
        # Mostrar proyectos guardados si existen
        if proyectos:
            proyectos_frame = Frame(main_select_frame, bg="#f5f5f5", relief=SOLID, borderwidth=1)
            proyectos_frame.pack(fill=X, pady=(0, 15))
            
            Label(
                proyectos_frame,
                text="📚 Proyectos guardados anteriormente:",
                font=("Arial", 9, "bold"),
                bg="#f5f5f5"
            ).pack(anchor=W, padx=10, pady=(10, 5))
            
            # Lista de proyectos (máximo 5 más recientes)
            proyectos_ordenados = sorted(
                proyectos.items(),
                key=lambda x: x[1].get('fecha_ultimo_acceso', ''),
                reverse=True
            )[:5]
            
            for ruta_proy, datos_proy in proyectos_ordenados:
                btn_proy = Button(
                    proyectos_frame,
                    text=f"📁 {os.path.basename(ruta_proy)}",
                    command=lambda r=ruta_proy: self.seleccionar_proyecto_guardado(r),
                    bg="#e3f2fd",
                    fg="#1976d2",
                    font=("Arial", 9),
                    anchor=W,
                    padx=10,
                    pady=5,
                    cursor="hand2"
                )
                btn_proy.pack(fill=X, padx=10, pady=2)
                
                Label(
                    proyectos_frame,
                    text=f"   {ruta_proy}",
                    font=("Arial", 8),
                    bg="#f5f5f5",
                    fg="#666"
                ).pack(anchor=W, padx=20, pady=(0, 5))
            
            Label(
                proyectos_frame,
                text="O selecciona una carpeta nueva:",
                font=("Arial", 9, "italic"),
                bg="#f5f5f5",
                fg="#666"
            ).pack(anchor=W, padx=10, pady=(5, 10))
        
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
        
        # Botón para continuar (siempre visible)
        btn_continuar = Button(
            self.btn_frame,
            text="🚀 CONTINUAR",
            command=self.continuar_o_configurar,
            bg="#4caf50",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=40,
            pady=15,
            cursor="hand2",
            relief=RAISED,
            borderwidth=3
        )
        btn_continuar.pack(pady=20)
        
        Label(
            self.btn_frame,
            text="💡 Haz clic en el botón verde de arriba para continuar",
            font=("Arial", 10),
            fg="#666"
        ).pack(pady=(0, 10))
        
        # Enter en el entry también continúa
        ruta_entry.bind("<Return>", lambda e: self.continuar_o_configurar())
    
    def continuar_o_configurar(self):
        """Continúa directamente a la vista principal"""
        ruta = self.ruta_proyecto.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto")
            return
        
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "La carpeta seleccionada no existe")
            return
        
        if not os.path.isdir(ruta):
            messagebox.showerror("Error", "La ruta seleccionada no es una carpeta válida")
            return
        
        self.ruta_proyecto_usuario = ruta
        os.chdir(ruta)
        
        # Guardar proyecto en historial
        guardar_proyecto(ruta)
        
        # Si es primera vez, hacer configuración inicial automáticamente
        if es_primera_vez():
            # Configurar Git automáticamente sin preguntar
            self.log("\n🔧 Configurando Git automáticamente...", "info")
            configurar_git_automatico()
            
            # Inicializar Git si no existe
            if not os.path.exists(".git"):
                self.log("📦 Inicializando repositorio Git...", "info")
                ejecutar_comando("git init")
                self.log("✓ Repositorio inicializado", "success")
            
            # Guardar configuración
            guardar_configuracion({
                'configurado': True,
                'url_remoto': None,
                'ruta_proyecto': ruta
            })
        
        self.log(f"\n✓ Carpeta seleccionada: {ruta}", "success")
        self.log("✓ Proyecto guardado en historial", "success")
        self.mostrar_interfaz_principal()
    
    def continuar_con_carpeta(self):
        """Continúa con la carpeta seleccionada"""
        ruta = self.ruta_proyecto.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto")
            return
        
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "La carpeta seleccionada no existe")
            return
        
        # Validación de seguridad: verificar que es una carpeta válida
        if not os.path.isdir(ruta):
            messagebox.showerror("Error", "La ruta seleccionada no es una carpeta válida")
            return
        
        self.ruta_proyecto_usuario = ruta
        os.chdir(ruta)
        
        # Guardar proyecto en historial
        url = self.url_remoto.get().strip()
        if url and url != "https://github.com/usuario/repositorio.git":
            guardar_proyecto(ruta, url)
        else:
            guardar_proyecto(ruta)
        
        self.log(f"\n✓ Carpeta seleccionada: {ruta}", "success")
        self.log("✓ Proyecto guardado en historial", "success")
        self.mostrar_interfaz_principal()
    
    def buscar_carpeta(self):
        """Abre diálogo para seleccionar carpeta"""
        carpeta = filedialog.askdirectory(
            title="Selecciona la carpeta de TU PROYECTO",
            initialdir=os.path.expanduser("~")
        )
        if carpeta:
            # Validación de seguridad
            if not os.path.isdir(carpeta):
                messagebox.showerror("Error", "La ruta seleccionada no es una carpeta válida")
                return
            self.ruta_proyecto.set(carpeta)
            self.log(f"✓ Carpeta seleccionada: {carpeta}", "success")
    
    def seleccionar_proyecto_guardado(self, ruta):
        """Selecciona un proyecto del historial"""
        # Validación de seguridad
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "El proyecto ya no existe en esa ubicación")
            return
        
        if not os.path.isdir(ruta):
            messagebox.showerror("Error", "La ruta no es una carpeta válida")
            return
        
        self.ruta_proyecto.set(ruta)
        self.ruta_proyecto_usuario = ruta
        os.chdir(ruta)
        
        # Cargar datos del proyecto
        proyectos = cargar_proyectos()
        if ruta in proyectos and proyectos[ruta].get('url_remoto'):
            self.url_remoto.set(proyectos[ruta]['url_remoto'])
        
        # Actualizar fecha de acceso
        guardar_proyecto(ruta, proyectos.get(ruta, {}).get('url_remoto'))
        
        self.log(f"\n✓ Proyecto cargado: {ruta}", "success")
        self.mostrar_interfaz_principal()
    
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
        
        # Guardar proyecto en historial
        guardar_proyecto(ruta, url)
        
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
    
    def consultar_estado_git(self):
        """Consulta el estado de Git para ver qué hay configurado"""
        ruta = self.ruta_proyecto_usuario or os.getcwd()
        
        # Verificar si es un repositorio Git
        if os.path.exists(os.path.join(ruta, ".git")):
            self.log("✓ Repositorio Git detectado", "success")
            
            # Consultar remoto
            exito, remotos, _ = ejecutar_comando("git remote -v")
            if exito and remotos.strip():
                self.log(f"✓ Remoto configurado: {remotos.split()[1] if remotos else 'N/A'}", "success")
            else:
                self.log("⚠ No hay remoto configurado", "warning")
            
            # Consultar rama actual
            exito, rama, _ = ejecutar_comando("git branch --show-current")
            if exito and rama.strip():
                self.log(f"✓ Rama actual: {rama.strip()}", "success")
            
            # Consultar cambios pendientes
            exito, cambios, _ = ejecutar_comando("git status --porcelain")
            if exito and cambios.strip():
                num_cambios = len(cambios.strip().split('\n'))
                self.log(f"ℹ {num_cambios} archivo(s) con cambios pendientes", "info")
            else:
                self.log("ℹ No hay cambios pendientes", "info")
        else:
            self.log("⚠ No es un repositorio Git (se inicializará automáticamente)", "warning")
    
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
        
        # Consultar Git para ver qué hay configurado
        self.consultar_estado_git()
        
        # Frame de información
        info_frame = Frame(self.btn_frame, bg="#e3f2fd", relief=SOLID, borderwidth=1)
        info_frame.pack(pady=(0, 15), fill=X)
        
        info_text = (
            "💡 ¿Qué hace cada botón?\n"
            "• Botón AZUL: Agrega TODOS los archivos, guarda y sube\n"
            "• Botón NARANJA: Selecciona archivos específicos que tú elijas"
        )
        
        Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            bg="#e3f2fd",
            fg="#1976d2",
            justify=LEFT
        ).pack(padx=10, pady=8, anchor=W)
        
        # Botón principal - TODOS los archivos
        btn_principal = Button(
            self.btn_frame,
            text="🔄 TODOS LOS ARCHIVOS\n(Agregar + Guardar + Subir)",
            command=self.actualizar_automatico,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=40,
            pady=15,
            cursor="hand2",
            justify=CENTER
        )
        btn_principal.pack(pady=10)
        
        # Botón secundario - Archivos específicos
        btn_especificos = Button(
            self.btn_frame,
            text="➕ SELECCIONAR ARCHIVOS ESPECÍFICOS\n(Solo los que tú elijas)",
            command=self.seleccionar_archivos_especificos,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=12,
            cursor="hand2",
            justify=CENTER
        )
        btn_especificos.pack(pady=5)
    
    
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
        
        # PASO 2: Commit con mensaje del usuario
        self.log("\n💾 PASO 2: Guardando cambios...", "info")
        self.log("   Necesitamos un mensaje para guardar tus cambios", "info")
        
        mensaje = self.pedir_mensaje_commit()
        if not mensaje:
            self.log("   ⚠ Guardado cancelado", "warning")
            return
        
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
                self.log("   ⏳ Por favor espera, esto puede tardar unos segundos...", "info")
                self.log("   Comando: git push origin main", "info")
                self.root.update()  # Actualizar la interfaz para mostrar el mensaje
                
                # Ejecutar push en un hilo separado para no bloquear la interfaz
                def hacer_push():
                    # Verificar primero qué rama existe
                    exito_rama, rama_actual, _ = ejecutar_comando("git branch --show-current")
                    rama = rama_actual.strip() if exito_rama and rama_actual.strip() else "main"
                    
                    self.root.after(0, lambda: self.log(f"   📍 Rama actual: {rama}", "info"))
                    
                    # Verificar si hay commits para subir
                    exito_status, status, _ = ejecutar_comando("git status")
                    self.root.after(0, lambda: self.log(f"   📊 Estado: {status[:100] if status else 'Sin información'}", "info"))
                    
                    # Intentar push con la rama actual
                    self.root.after(0, lambda: self.log(f"   🔄 Subiendo a la rama '{rama}'...", "info"))
                    exito, salida, error = ejecutar_comando(f"git push origin {rama}")
                    
                    # Si falla, intentar con main
                    if not exito:
                        self.root.after(0, lambda: self.log("   ⚠ Intentando con 'main'...", "warning"))
                        exito, salida, error = ejecutar_comando("git push origin main")
                    
                    # Si aún falla, intentar con master
                    if not exito:
                        self.root.after(0, lambda: self.log("   ⚠ Intentando con 'master'...", "warning"))
                        exito, salida, error = ejecutar_comando("git push origin master")
                    
                    # Mostrar salida completa para debugging
                    if salida:
                        self.root.after(0, lambda: self.log(f"   📤 Salida: {salida[:300]}", "info"))
                    if error:
                        self.root.after(0, lambda: self.log(f"   ⚠ Error: {error[:300]}", "warning"))
                    
                    # Actualizar interfaz desde el hilo principal
                    if exito:
                        # Verificar que realmente se subió
                        exito_verificar, remoto_info, _ = ejecutar_comando("git remote -v")
                        self.root.after(0, lambda: self.log("   ✓ ¡Cambios subidos a GitHub exitosamente!", "success"))
                        self.root.after(0, lambda: self.log("   ✓ Tu código ya está disponible en internet", "success"))
                        if remoto_info:
                            self.root.after(0, lambda: self.log(f"   🔗 Repositorio: {remoto_info.split()[1] if len(remoto_info.split()) > 1 else 'N/A'}", "info"))
                        self.root.after(0, lambda: messagebox.showinfo("Éxito", "¡Cambios subidos a GitHub correctamente!\n\nTu código ya está disponible en internet."))
                    else:
                        self.root.after(0, lambda: self.log("   ✗ Error al subir a GitHub", "error"))
                        mensaje_error = f"No se pudo subir a GitHub.\n\n"
                        if error:
                            mensaje_error += f"Error: {error[:300]}\n\n"
                        if salida:
                            mensaje_error += f"Salida: {salida[:200]}\n\n"
                        mensaje_error += "Verifica:\n• Tu conexión a internet\n• Tus credenciales de GitHub\n• Que el repositorio remoto esté configurado correctamente"
                        self.root.after(0, lambda: self.log("   💡 Verifica tu conexión a internet y tus credenciales", "info"))
                        self.root.after(0, lambda: messagebox.showerror("Error", mensaje_error))
                
                # Iniciar el push en un hilo separado
                thread = threading.Thread(target=hacer_push, daemon=True)
                thread.start()
                
                # Actualizar la interfaz periódicamente mientras se ejecuta
                def actualizar_interfaz():
                    if thread.is_alive():
                        self.root.update()
                        self.root.after(100, actualizar_interfaz)
                
                actualizar_interfaz()
            else:
                self.log("\n⚠ Push cancelado por el usuario", "warning")
        else:
            self.log("\n⚠ No hay repositorio configurado para subir", "warning")
            self.log("   💡 Puedes configurar GitHub después si lo necesitas", "info")
        
        self.log("\n" + "="*60, "success")
        self.log("✅ ¡COMPLETADO!", "success")
        self.log("="*60, "success")
    
    def pedir_mensaje_commit(self):
        """Pide el mensaje del commit"""
        dialog = Toplevel(self.root)
        dialog.title("📝 Mensaje del Commit")
        dialog.geometry("550x220")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (220 // 2)
        dialog.geometry(f"550x220+{x}+{y}")
        
        mensaje_var = StringVar()
        mensaje_var.set(f"Actualización - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        Label(dialog, text="📝 Escribe el mensaje para tu commit:", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        
        Label(dialog, text="Ejemplo: 'Agregué nueva funcionalidad' o 'Corregí errores'", 
              font=("Arial", 9), fg="#666").pack(pady=(0, 5))
        
        entry = Entry(dialog, textvariable=mensaje_var, width=60, font=("Arial", 11))
        entry.pack(pady=10, padx=20)
        entry.select_range(0, END)
        entry.focus()
        
        resultado = [None]
        
        def aceptar():
            resultado[0] = mensaje_var.get().strip()
            if not resultado[0]:
                resultado[0] = f"Actualización - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            dialog.destroy()
        
        def cancelar():
            resultado[0] = None
            dialog.destroy()
        
        btn_frame = Frame(dialog)
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="✓ Aceptar", command=aceptar, bg="#4caf50", fg="white", 
               font=("Arial", 11, "bold"), padx=20, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
        Button(btn_frame, text="✗ Cancelar", command=cancelar, bg="#f44336", fg="white",
               font=("Arial", 10), padx=20, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
        
        entry.bind("<Return>", lambda e: aceptar())
        entry.bind("<Escape>", lambda e: cancelar())
        
        dialog.wait_window()
        return resultado[0]
    
    def seleccionar_archivos_especificos(self):
        """Permite seleccionar archivos específicos para agregar con checkboxes"""
        # Verificar que hay una carpeta seleccionada
        if not self.ruta_proyecto_usuario:
            ruta = self.ruta_proyecto.get().strip()
            if not ruta or not os.path.exists(ruta):
                messagebox.showerror("Error", "Debes seleccionar la carpeta de tu proyecto primero")
                self.seleccionar_carpeta_proyecto_inicio()
                return
            self.ruta_proyecto_usuario = ruta
        
        os.chdir(self.ruta_proyecto_usuario)
        
        # Obtener lista de archivos modificados
        exito, cambios, _ = ejecutar_comando("git status --porcelain")
        if not exito or not cambios.strip():
            messagebox.showinfo("Info", "No hay archivos modificados para seleccionar")
            return
        
        # Crear ventana de selección más grande
        dialog = Toplevel(self.root)
        dialog.title("📁 Seleccionar Archivos Específicos")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"800x600+{x}+{y}")
        
        # Título
        Label(dialog, text="📁 Selecciona los archivos que quieres agregar:", 
              font=("Arial", 14, "bold")).pack(pady=(20, 15))
        
        # Frame principal con scrollbar
        main_frame = Frame(dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Canvas para scroll
        canvas = Canvas(main_frame, bg="white")
        scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Agregar archivos con checkboxes
        archivos_lista = []
        checkboxes_vars = {}
        
        for linea in cambios.strip().split('\n'):
            if linea.strip():
                archivo = linea[3:].strip()  # Quitar el estado (M, A, etc.)
                archivos_lista.append(archivo)
                
                # Crear frame para cada archivo
                file_frame = Frame(scrollable_frame, bg="white", relief=SOLID, borderwidth=1)
                file_frame.pack(fill=X, padx=5, pady=3)
                
                # Checkbox
                var = BooleanVar(value=True)  # Todos seleccionados por defecto
                checkboxes_vars[archivo] = var
                
                checkbox = Checkbutton(
                    file_frame,
                    text=archivo,
                    variable=var,
                    font=("Consolas", 10),
                    bg="white",
                    anchor=W,
                    justify=LEFT
                )
                checkbox.pack(fill=X, padx=10, pady=5)
        
        # Pack canvas y scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Botones de acción
        btn_frame = Frame(dialog)
        btn_frame.pack(pady=20)
        
        # Botón seleccionar todos
        def seleccionar_todos():
            for var in checkboxes_vars.values():
                var.set(True)
        
        # Botón deseleccionar todos
        def deseleccionar_todos():
            for var in checkboxes_vars.values():
                var.set(False)
        
        Button(btn_frame, text="✓ Seleccionar Todos", command=seleccionar_todos,
               bg="#2196F3", fg="white", font=("Arial", 10), 
               padx=15, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="✗ Deseleccionar Todos", command=deseleccionar_todos,
               bg="#FF9800", fg="white", font=("Arial", 10), 
               padx=15, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
        
        resultado = [None]
        
        def aceptar():
            seleccionados = [archivo for archivo, var in checkboxes_vars.items() if var.get()]
            if seleccionados:
                resultado[0] = seleccionados
                dialog.destroy()
            else:
                messagebox.showwarning("Advertencia", "Debes seleccionar al menos un archivo")
        
        def cancelar():
            resultado[0] = None
            dialog.destroy()
        
        Button(btn_frame, text="✓ Agregar Seleccionados", command=aceptar, 
               bg="#4caf50", fg="white", font=("Arial", 12, "bold"), 
               padx=25, pady=10, cursor="hand2").pack(side=LEFT, padx=10)
        Button(btn_frame, text="✗ Cancelar", command=cancelar, 
               bg="#f44336", fg="white", font=("Arial", 11), 
               padx=25, pady=10, cursor="hand2").pack(side=LEFT, padx=5)
        
        # Habilitar scroll con rueda del mouse
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        dialog.wait_window()
        
        if resultado[0]:
            self.log("\n" + "="*60, "info")
            self.log("➕ AGREGANDO ARCHIVOS ESPECÍFICOS", "info")
            self.log("="*60, "info")
            self.log(f"\n📁 Archivos seleccionados: {len(resultado[0])}", "info")
            
            # Agregar cada archivo seleccionado
            for archivo in resultado[0]:
                self.log(f"   Agregando: {archivo}", "info")
                ejecutar_comando(f'git add "{archivo}"')
            
            self.log("\n✓ Archivos agregados", "success")
            
            # Preguntar si hacer commit
            respuesta = messagebox.askyesno(
                "¿Guardar cambios?",
                f"¿Deseas guardar estos {len(resultado[0])} archivo(s) con un commit?"
            )
            
            if respuesta:
                mensaje = self.pedir_mensaje_commit()
                if mensaje:
                    self.log(f"\n💾 Guardando con mensaje: {mensaje}", "info")
                    exito, _, error = ejecutar_comando(f'git commit -m "{mensaje}"')
                    if exito:
                        self.log("✓ Cambios guardados", "success")
                        
                        # Preguntar push
                        config = cargar_configuracion()
                        if config.get('url_remoto'):
                            respuesta_push = messagebox.askyesno(
                                "¿Subir a GitHub?",
                                f"¿Deseas subir estos cambios a GitHub?\n\nRepositorio: {config['url_remoto']}"
                            )
                            if respuesta_push:
                                self.log("\n☁️ Subiendo a GitHub...", "info")
                                self.log("   ⏳ Por favor espera, esto puede tardar unos segundos...", "info")
                                self.log("   Comando: git push origin main", "info")
                                self.root.update()  # Actualizar la interfaz para mostrar el mensaje
                                
                                # Ejecutar push en un hilo separado para no bloquear la interfaz
                                def hacer_push_archivos():
                                    # Intentar con main primero
                                    exito, salida, error = ejecutar_comando("git push origin main")
                                    if not exito:
                                        self.root.after(0, lambda: self.log("   ⚠ Intentando con 'master'...", "warning"))
                                        self.root.update()
                                        exito, salida, error = ejecutar_comando("git push origin master")
                                    
                                    # Actualizar interfaz desde el hilo principal
                                    if exito:
                                        self.root.after(0, lambda: self.log("   ✓ ¡Cambios subidos a GitHub exitosamente!", "success"))
                                        self.root.after(0, lambda: self.log("   ✓ Tu código ya está disponible en internet", "success"))
                                        self.root.after(0, lambda: messagebox.showinfo("Éxito", "¡Cambios subidos a GitHub correctamente!\n\nTu código ya está disponible en internet."))
                                    else:
                                        self.root.after(0, lambda: self.log("   ✗ Error al subir a GitHub", "error"))
                                        if error:
                                            self.root.after(0, lambda: self.log(f"   Detalles: {error[:200]}", "error"))
                                        self.root.after(0, lambda: self.log("   💡 Verifica tu conexión a internet y tus credenciales", "info"))
                                        self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo subir a GitHub.\n\nError: {error[:200] if error else 'Error desconocido'}\n\nVerifica tu conexión a internet y tus credenciales de GitHub."))
                                
                                # Iniciar el push en un hilo separado
                                thread_push = threading.Thread(target=hacer_push_archivos, daemon=True)
                                thread_push.start()
                                
                                # Actualizar la interfaz periódicamente mientras se ejecuta
                                def actualizar_interfaz_push():
                                    if thread_push.is_alive():
                                        self.root.update()
                                        self.root.after(100, actualizar_interfaz_push)
                                
                                actualizar_interfaz_push()
                            else:
                                self.log("\n⚠ Push cancelado por el usuario", "warning")
                        else:
                            self.log("\n⚠ No hay repositorio configurado para subir", "warning")
                    else:
                        self.log(f"✗ Error: {error}", "error")
            
            self.log("\n" + "="*60, "success")
            self.log("✅ ¡COMPLETADO!", "success")
            self.log("="*60, "success")


def main():
    root = Tk()
    app = GitAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
