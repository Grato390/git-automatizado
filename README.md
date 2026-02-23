# 🚀 Automatización de Git - Ultra Simplificada

Sistema **100% automático** para Git. Un solo clic y hace TODO.

## ✨ Características

- ✅ **Un solo botón**: Hace `git add`, `commit` y `push` automáticamente
- ✅ **Configuración inicial automática**: Solo pide la URL del repo
- ✅ **Interfaz gráfica simple**: Sin complicaciones
- ✅ **Todo automático**: No necesitas escribir comandos

## 🚀 Uso

### ⭐ MÉTODO MÁS FÁCIL: Usar el .EXE

**¡Ya está creado y listo!** Solo haz doble clic en:
- **`dist\Git-Automation.exe`**

**Ventajas del .exe:**
- ✅ No necesitas Python instalado
- ✅ No necesitas activar nada
- ✅ Solo doble clic y funciona
- ✅ Puedes copiarlo a cualquier lugar
- ✅ Puedes subirlo a GitHub y compartirlo

### Método alternativo: Scripts

1. **Doble clic en `ejecutar.vbs`** (recomendado - sin mostrar consola)
   O si prefieres: **Doble clic en `ejecutar.bat`**
2. **Encuentra la URL de tu repositorio en GitHub:**
   - Ve a tu repositorio en GitHub
   - Haz clic en el botón verde **"Code"** (arriba a la derecha)
   - Selecciona la pestaña **"HTTPS"**
   - Copia la URL que aparece (ejemplo: `https://github.com/usuario/repositorio.git`)
3. Pega la URL en el campo de la aplicación
4. Clic en **"CONFIGURAR Y AUTOMATIZAR TODO"**
5. ¡Listo! El sistema hace todo automáticamente

**Ejemplo de URL:**
```
https://github.com/Grato390/git-automatizado.git
```

### Uso diario

1. **Doble clic en `ejecutar.bat`**
2. Clic en **"ACTUALIZAR TODO"**
3. ¡Listo! Hace `git add`, `commit` y `push` automáticamente

## 📁 Archivos

```
automatizar git/
├── dist/
│   └── Git-Automation.exe   # ⭐ ARCHIVO .EXE (¡Ya está creado!)
├── git_automation_gui.py     # Script principal (GUI)
├── ejecutar.vbs              # Ejecutar sin consola (recomendado)
├── ejecutar.bat              # Ejecutar (doble clic)
├── crear_exe.bat             # Crear .exe (si necesitas regenerarlo)
├── requirements.txt          # Dependencias
├── .gitignore               # Archivos a ignorar
└── README.md                # Este archivo
```

## ⚙️ Instalación (Ya está hecho)

Todo ya está instalado y listo. Solo ejecuta `ejecutar.vbs` o `ejecutar.bat`

## 📦 Crear Archivo .EXE (Opcional)

Si quieres crear un archivo .exe para distribuir fácilmente:

1. **Doble clic en `crear_exe.bat`**
2. Espera a que termine (puede tardar 1-2 minutos)
3. El archivo `.exe` estará en la carpeta `dist\`
4. Puedes copiar ese `.exe` a cualquier lugar y ejecutarlo directamente

**Ventajas del .exe:**
- ✅ No necesitas Python instalado
- ✅ No necesitas activar el entorno virtual
- ✅ Solo haz doble clic y funciona
- ✅ Puedes compartirlo fácilmente

## 🎯 ¿Qué hace automáticamente?

- ✅ `git init` (si no existe)
- ✅ Configura remoto (si proporcionas URL)
- ✅ `git add .` (agrega todos los cambios)
- ✅ `git commit` (con mensaje automático)
- ✅ `git push` (si hay remoto configurado)

## 💡 Notas

- Si no quieres hacer push, usa el botón "Solo Agregar Cambios"
- La primera vez solo pide la URL del repositorio
- Todo lo demás es automático

---

**¡Listo para usar! Solo haz doble clic en `ejecutar.bat`** 🚀
