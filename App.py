# 'freeze_support' es necesario para que 'multiprocessing' (usado por SynchronyService)
# funcione correctamente al crear un ejecutable especialmente en Windows.
from multiprocessing import freeze_support

# --- Importaciones de Componentes ---
from Controllers.ContactsController import ContactsController
import asyncio
import os
from Controllers.SynchronyController import SynchronyController
from Views.ListContactsView import list_contacts_view
from Views.isLoadingView import is_loading
from Views.MainMenuView import MainMenuView
from ConfigManager import ConfigManager
import FileManager
from ApiPinger import ping_api
# Importa la instancia única del estado global
from SharedState import global_state
# Importa el módulo que contiene las corutinas de las tareas en segundo plano
import BackgroundTasks
from Views.ManageFileMenu import manage_files_menu
from Views.ManageConfigMenuView import manage_config_menu

# --- Funciones de Utilidad ---

def clear():
    """Función de utilidad para limpiar la consola."""
    os.system("cls" if os.name == "nt" else "clear")

async def blocking_input(prompt):
    """
    Ejecuta la función 'input' (que es síncrona y bloqueante) en un hilo separado.
    Esto es CRUCIAL para que 'input()' no congele todo el bucle de asyncio,
    permitiendo que las tareas en segundo plano (como el descargador) sigan funcionando
    mientras el programa espera la entrada del usuario.
    """
    # Obtiene el bucle de eventos actual
    loop = asyncio.get_event_loop()
    # 'loop.run_in_executor(None, ...)' usa el pool de hilos por defecto
    # para ejecutar la función bloqueante 'input' con el 'prompt' dado.
    return await loop.run_in_executor(None, input, prompt)


# --- Lógica de Opciones de Menú ---

def list_contacts():
    """
    Función SÍNCRONA (normal) que agrupa la lógica de listar contactos.
    Es síncrona porque 'ContactsController' y 'ContactRepository'
    leen archivos de forma bloqueante.
    Será llamada usando 'run_in_executor'.
    """
    contacts_controller = ContactsController()
    contacts = contacts_controller.get_all_contacts()
    list_contacts_view(contacts)


async def selectMenu(option, config_manager):
    """
    Función asíncrona (corutina) que actúa como 'router' para el menú.
    Recibe la opción elegida y ejecuta la acción correspondiente.
    """
    if option == 1:
        clear()
        # Ejecuta la función síncrona 'list_contacts' en un hilo
        # para no bloquear el bucle de asyncio.
        await asyncio.get_event_loop().run_in_executor(None, list_contacts)
        await blocking_input("\nPresione Enter para volver al menú...")
    
    elif option == 2:
        clear()
        s_controller = SynchronyController()
        print("Iniciando sincronización manual...")

        # Llama al 'wrapper' asíncrono 'is_loading'.
        # 'is_loading' ejecutará 's_controller.synchronize' (que es bloqueante)
        # en un hilo separado, mostrando "Cargando..." mientras tanto.
        response = await is_loading(s_controller.synchronize)
        print("\n" + response)
        
        # Después de sincronizar, fuerza una actualización de la lista de archivos
        # para que el menú 'Administrar Archivos' muestre los cambios inmediatamente.
        await BackgroundTasks.refresh_file_list_once()

        await blocking_input("\nPresione Enter para volver al menú...")
    
    elif option == 3:
        # Llama a la corutina del submenú de gestión de archivos.
        await manage_files_menu(clear, global_state, blocking_input, FileManager, BackgroundTasks)
        
    elif option == 4:
        # Llama a la corutina del submenú de configuración.
        await manage_config_menu(config_manager, clear, blocking_input)
    
    elif option == 5:
        clear()
        # Llama a la corutina de 'ping_api', pasándole 'True'
        # para que imprima los resultados en la pantalla.
        await ping_api(True)
        await blocking_input("\nPresione Enter para volver al menú...")
        
    elif option == 6:
        clear()
        print("Saliendo...")
        # Devuelve 'False' para indicar al bucle principal que debe detenerse.
        return False 
    
    # Devuelve 'True' para indicar al bucle principal que continúe.
    return True 

# --- Punto de Entrada Principal (Asíncrono) ---

async def main():
    """
    La corutina principal que orquesta toda la aplicación.
    """
    # Asegura que los directorios necesarios existan.
    os.makedirs("db", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    config = ConfigManager()
    
    # --- LANZAR TAREAS EN SEGUNDO PLANO ---
    print("Iniciando tareas en segundo plano...")
    # 'asyncio.create_task' agenda las corutinas para que se ejecuten
    # concurrentemente (en "segundo plano") en el bucle de eventos.
    
    # Tarea 1: El descargador automático (ej. cada 5 min)
    downloader_task = asyncio.create_task(BackgroundTasks.run_downloader(config))
    # Tarea 2: El vigilante de archivos (ej. cada 5 seg)
    watcher_task = asyncio.create_task(BackgroundTasks.run_file_watcher())
    
    # Da un breve momento para que las tareas se inicien
    # (y actualicen la lista inicial de archivos)
    await asyncio.sleep(1) 
    
    # --- BUCLE PRINCIPAL DEL MENÚ ---
    while True:
        clear()
        # Llama a la vista del menú (que usa 'blocking_input' asíncrono)
        option = await MainMenuView(clear, blocking_input)
        
        # Llama al 'router' del menú
        keep_running = await selectMenu(option, config)
        
        # Si 'selectMenu' (Opción 6) devolvió 'False', rompe el bucle.
        if not keep_running:
            break
    
    # --- APAGADO ---
    print("Deteniendo tareas en segundo plano...")
    # 'cancel()' envía una excepción 'CancelledError' a las tareas,
    # permitiéndoles un cierre limpio (como se ve en sus bucles 'try...except').
    downloader_task.cancel()
    watcher_task.cancel()

    print("Aplicación cerrada.")

# --- Bloque de Ejecución ---
if __name__ == "__main__":
    # Llama a 'freeze_support()' al inicio, por si la app es compilada.
    freeze_support()
    try:
        # 'asyncio.run(main())' es la forma moderna de iniciar
        # una aplicación asyncio. Crea el bucle de eventos,
        # ejecuta 'main()' hasta que termine, y cierra el bucle.
        asyncio.run(main())
    except KeyboardInterrupt:
        # Captura Ctrl+C para un cierre más amigable.
        print("\nCierre forzado por el usuario.")