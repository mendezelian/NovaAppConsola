import asyncio
import os
import time
# Importa las clases necesarias
from ConfigManager import ConfigManager
from Services.SynchronyService import SynchronyService
from SharedState import global_state # Importa el objeto de estado global

# Define las rutas como constantes
DB_PATH = "db"
LOGS_PATH = "logs"

# Define una corutina (tarea asíncrona) que se ejecutará en segundo plano
async def run_downloader(config_manager):
    """
    Tarea en segundo plano: se ejecuta cada X minutos para 
    descargar nuevos datos de la API.
    """
    log = None # Inicializa la variable del archivo log
    try:
        # Abre el archivo de log en modo 'append' (añadir al final)
        with open(f"{LOGS_PATH}\\logs.log", 'a', encoding='utf-8') as log:
            
            # Instancia el servicio que contiene la lógica de sincronización
            s_service = SynchronyService()
            # Obtiene el bucle de eventos de asyncio
            loop = asyncio.get_event_loop()
            log.write("[Downloader] Tarea de descarga automática iniciada.\n")
            log.flush() # Asegura que se escriba en el disco
            
            # Bucle principal: se ejecuta indefinidamente hasta que se cancele
            while True:
                try:
                    # 1. Obtener el intervalo desde el config
                    # Se obtiene DENTRO del bucle, para que los cambios de config
                    # se apliquen en la siguiente iteración.
                    interval_min = config_manager.get_download_interval()
                    log.write(f"[Downloader] Próxima ejecución en {interval_min} minutos...\n")
                    log.flush()
                    
                    # 3. Dormir (de forma no bloqueante)
                    # La primera vez duerme antes de ejecutar.
                    # 'asyncio.sleep' pausa esta tarea, pero permite que otras
                    # (como la UI) sigan funcionando.
                    await asyncio.sleep(interval_min * 60)
                    
                    log.write(f"\n[Downloader] {time.strftime('%H:%M:%S')} - Iniciando descarga automática...\n")
                    log.flush()
                    
                    # 2. Ejecutar la sincronización (que es bloqueante) en un hilo
                    # 's_service.run_process' es una función normal (síncrona)
                    # 'loop.run_in_executor' la ejecuta en un hilo separado
                    # para no congelar el bucle de asyncio.
                    await loop.run_in_executor(None, s_service.run_process)
                    
                    # 3. Forzar a la otra tarea (File Watcher) a que se actualice
                    # para que el usuario vea los nuevos archivos de timestamp
                    # (Esta función también debe estar definida en el mismo contexto)
                    await run_file_watcher(force_update=True)
                    
                    log.write(f"[Downloader] {time.strftime('%H:%M:%S')} - Descarga automática completada.\n")
                    log.flush()
                    
                # Se lanza si la tarea es cancelada (ej. al salir de la app)
                except asyncio.CancelledError:
                    log.write("[Downloader] Tarea de descarga detenida.\n")
                    log.flush()
                    break # Rompe el 'while True'
                    
                # Captura cualquier otro error (ej. de red) durante la sincronización
                except Exception as e:
                    log.write(f"[Downloader] Error en la tarea de descarga: {e}\n")
                    log.flush()
                    # Esperar un poco antes de reintentar en caso de error
                    await asyncio.sleep(60)
                    
    except IOError as e:
        # Error si no se puede abrir el archivo de log
        print(f"Error al Guardar Logs {e}")
    finally:
        # Se asegura de cerrar el archivo de log si se abrió
        if log:
            log.close()

# Define la segunda tarea en segundo plano
async def run_file_watcher(force_update=False):
    log = None
    try:
        # Abre el log en modo escritura ('w'), borrando el contenido anterior.
        # (Esto puede ser intencional o un bug, el downloader usa 'a')
        with open(f"{LOGS_PATH}\\logs.log", "w", encoding="utf-8") as log:
            """
            Tarea en segundo plano: vigila el directorio 'db' 
            y actualiza el estado global.
            """
            loop = asyncio.get_event_loop()
            # Estado local para comparar si la lista de archivos ha cambiado
            last_files = []
            log.write("[FileWatcher] Tarea de vigilancia de archivos iniciada.\n")
            log.flush()
            
            # Bucle principal de la tarea
            while True:
                try:
                    # 1. Obtener la lista de archivos (es I/O bloqueante)
                    # 'os.listdir' es síncrono. Se ejecuta en un hilo.
                    # 'lambda' se usa para pasar la función al ejecutor.
                    files = await loop.run_in_executor(
                        None, 
                        lambda: [f for f in os.listdir(DB_PATH) if f.endswith('.json')]
                    )
                    files.sort() # Ordenar para que la comparación sea fiable

                    # 2. Actualizar el estado global SOLO si hay cambios
                    # O si otra tarea (el downloader) ha forzado la actualización.
                    if files != last_files or force_update:
                        # Actualiza el objeto de estado compartido
                        global_state.set_files(files)
                        # Actualiza la caché local
                        last_files = files
                        
                        if force_update:
                            log.write("[FileWatcher] Lista de archivos actualizada (forzado).\n")
                            log.flush()
                            force_update = False # Resetea el flag
                    
                    # 3. Dormir por un corto tiempo (no bloqueante)
                    await asyncio.sleep(5) # Vigila cada 5 segundos
                    
                except asyncio.CancelledError:
                    log.write("[FileWatcher] Tarea de vigilancia detenida.\n")
                    log.flush()
                    break # Rompe el 'while True'
                except Exception as e:
                    log.write(f"[FileWatcher] Error en la tarea de vigilancia: {e}\n")
                    log.flush()
                    # Espera más tiempo si hay un error
                    await asyncio.sleep(10)
    except IOError as e:
        print(f"Error al Guardar Logs: {e}")
    finally:
        if log:
            log.close()

# Define una función de un solo uso para cargar el estado inicial
async def refresh_file_list_once():
    """
    Igual que 'run_file_watcher' pero se ejecuta una sola vez.
    Útil para cargar el estado al inicio de la aplicación.
    """
    try:
        loop = asyncio.get_event_loop()
        # Obtiene la lista de archivos (bloqueante, en un hilo)
        files = await loop.run_in_executor(
            None,
            lambda: [f for f in os.listdir(DB_PATH) if f.endswith('.json')]
        )
        files.sort()
        # Establece el estado global inicial
        global_state.set_files(files)
    except Exception as e:
        print(f"[FileWatcher] Error al actualizar archivos una vez: {e}")