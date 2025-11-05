import os
import json
# Subprocess es necesario para ejecutar programas externos (como 'notepad' o 'nano')
import subprocess
# Platform nos deja saber el sistema operativo (Windows, Linux, etc.)
import platform
import sys

# Define la ruta del directorio base para todos los archivos
DB_PATH = "db"

def _get_editor():
    """
    Función auxiliar privada para determinar el editor de texto de consola.
    """
    # Si el sistema es Windows, usa 'notepad'.
    if platform.system() == "Windows":
        return "notepad"
    
    # Para Linux/MacOS, busca un editor en orden de preferencia.
    for editor in ["nano", "vim", "vi"]:
        # Comprueba si el comando del editor existe en el PATH del sistema.
        # 'which' es un comando de Unix; '>/dev/null 2>&1' oculta la salida.
        if os.system(f"which {editor} > /dev/null 2>&1") == 0:
            return editor
            
    # Si no se encuentra ninguno, usa 'vi' como último recurso.
    return "vi"

def view_db_file(filename):
    """
    Función para ver (imprimir) el contenido de un archivo JSON.
    Esta función es síncrona pero rápida (solo lee).
    """
    # Construye la ruta completa al archivo (ej: "db/clients.json").
    filepath = os.path.join(DB_PATH, filename)
    try:
        # Abre y lee el archivo.
        with open(filepath, 'r', encoding='utf-8') as f:
            # 'json.load' convierte el texto del archivo en un objeto Python.
            data = json.load(f)
        
        # Imprime el encabezado y el contenido.
        print(f"--- Contenido de {filename} ---")
        # 'json.dumps' convierte el objeto Python de nuevo a un string JSON,
        # pero formateado (indent=2) y con caracteres UTF-8 (ensure_ascii=False).
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("---------------------------------")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

def delete_db_file(filename):
    """
    Función para eliminar un archivo de la base de datos.
    ¡IMPORTANTE: Esta función es BLOQUEANTE!
    Contiene un 'input()' que detiene el hilo de ejecución.
    Debe ser llamada con 'run_in_executor' en un entorno asyncio.
    """
    filepath = os.path.join(DB_PATH, filename)
    try:
        if not os.path.exists(filepath):
            print(f"Error: El archivo '{filename}' no se encontró.")
            return False
        
        # Esta llamada 'input()' es síncrona y bloqueante.
        # Detiene la ejecución aquí hasta que el usuario presione Enter.
        confirm = input(f"¿Seguro que quieres eliminar '{filename}'? (s/n): ").strip().lower()
        
        if confirm == 's':
            # Elimina el archivo del disco.
            os.remove(filepath)
            print(f"Archivo '{filename}' eliminado con éxito.")
            return True # Indicar éxito
        else:
            print("Eliminación cancelada.")
            return False # Indicar cancelación
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")
        return False

# --- NUEVAS FUNCIONES (BLOQUEANTES) ---
# Estas funciones deben ser llamadas con loop.run_in_executor()

def add_db_file(filename):
    """
    Crea un nuevo archivo JSON y lo abre en el editor.
    ¡IMPORTANTE: Esta función es BLOQUEANTE!
    Llama a 'subprocess.run' y espera a que el editor se cierre.
    """
    
    # Validación simple del nombre
    if not filename.endswith(".json"):
        print("Error: El nombre del archivo debe terminar en .json")
        return False
    
    filepath = os.path.join(DB_PATH, filename)
    
    # Comprobar si ya existe para no sobrescribir
    if os.path.exists(filepath):
        print(f"Error: El archivo '{filename}' ya existe.")
        return False
    
    try:
        # Crear un archivo JSON vacío pero válido (con llaves).
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("{\n\n}")
        
        print(f"Archivo '{filename}' creado. Abriendo editor...")
        
        # Abrir el editor. 'subprocess.run' es síncrono.
        # El script de Python se pausará aquí hasta que el usuario cierre el editor.
        editor = _get_editor()
        subprocess.run([editor, filepath])
        
        print(f"Edición de '{filename}' finalizada.")
        
        # Validar que el archivo sigue siendo un JSON válido
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f) # Intentar cargarlo
        
        print("El JSON es válido.")
        return True # Éxito
        
    # Se activa si 'json.load()' falla
    except json.JSONDecodeError:
        print("¡Error! El contenido guardado no es un JSON válido.")
        print(f"El archivo '{filename}' podría estar corrupto.")
        return False
    except Exception as e:
        print(f"Error al añadir archivo: {e}")
        return False

def edit_db_file(filename):
    """
    Abre un archivo JSON existente en el editor.
    ¡IMPORTANTE: Esta función es BLOQUEANTE!
    Llama a 'subprocess.run' y espera a que el editor se cierre.
    """
    filepath = os.path.join(DB_PATH, filename)
    if not os.path.exists(filepath):
        print(f"Error: El archivo '{filename}' no se encontró.")
        return False
    
    # Define la ruta del archivo de backup
    backup_path = filepath + ".bak"
    
    try:
        # 1. Crear un backup antes de editar
        with open(filepath, 'r', encoding='utf-8') as f_orig, open(backup_path, 'w', encoding='utf-8') as f_bak:
            f_bak.write(f_orig.read())
        
        print(f"Abriendo '{filename}' en el editor...")
        
        # 2. Abrir el editor (llamada bloqueante)
        editor = _get_editor()
        subprocess.run([editor, filepath])
        
        print(f"Edición de '{filename}' finalizada.")
        
        # 3. Validar el JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f) # Intentar cargar
        
        # 4. Si es válido, eliminar el backup
        print("El JSON es válido. Eliminando backup.")
        os.remove(backup_path)
        return True # Éxito
        
    # 5. Si el JSON es inválido (falla 'json.load()')
    except json.JSONDecodeError:
        print("¡Error! El contenido guardado no es un JSON válido.")
        print(f"Restaurando desde backup...")
        # Restaura el backup
        os.remove(filepath) # Eliminar archivo corrupto
        os.rename(backup_path, filepath) # Restaurar backup
        print("Archivo original restaurado.")
        return False
    
    # 6. Captura de otros errores
    except Exception as e:
        print(f"Error al editar archivo: {e}")
        # Informa al usuario que el backup existe
        if os.path.exists(backup_path):
            print(f"Se ha guardado un backup en '{backup_path}'")
        return False