# Define una función asíncrona (corutina) para gestionar el submenú de configuración
# Recibe:
# - config_manager: Una instancia del objeto que maneja la lectura/escritura de la config.
# - clear: La función para limpiar la consola.
# - blocking_input: La función asíncrona para pedir datos al usuario.
async def manage_config_menu(config_manager, clear, blocking_input):
    
    # Limpia la pantalla
    clear()
    
    # Muestra el título del menú
    print("--- CONFIGURACIÓN ---")
    
    # Muestra el estado actual de la configuración
    print("Configuración actual:")
    # Llama a un método del config_manager para obtener un string formateado
    # con los valores actuales (ej. URL, intervalo).
    print(config_manager.get_config_display())
    
    # Muestra las opciones disponibles en este submenú
    print("\nOpciones:")
    print("1. Cambiar URL de la API")
    print("2. Cambiar intervalo de descarga (minutos)")
    print("3. Volver al menú principal")
    
    # Pide al usuario que elija una opción (espera 'await' la entrada)
    choice = await blocking_input("Seleccione (1-3): ")
    
    # Si el usuario elige '1' (Cambiar URL)
    if choice == '1':
        # Pide la nueva URL
        new_url = await blocking_input("Ingrese la nueva URL de la API: ")
        
        # Comprueba que el usuario realmente escribió algo
        if new_url:
            # Si no está vacío, usa el config_manager para guardar la nueva URL
            config_manager.set_api_url(new_url)
        else:
            # Informa si el usuario presionó Enter sin escribir nada
            print("URL no puede estar vacía. No se realizaron cambios.")
    
    # Si el usuario elige '2' (Cambiar intervalo)
    elif choice == '2':
        # Pide el nuevo intervalo
        new_interval = await blocking_input("Nuevo intervalo en minutos (ej: 5): ")
        
        # Comprueba que el usuario escribió algo
        if new_interval:
            # Usa el config_manager para guardar el nuevo intervalo
            config_manager.set_download_interval(new_interval)
            print("El cambio se aplicará en la próxima ejecución de la tarea.")
    
    # La opción '3' (Volver) no necesita un 'elif' porque la función
    # simplemente terminará, volviendo al bucle principal que la llamó.
    
    # Si se realizó una acción (1 o 2), hace una pausa
    # para que el usuario pueda leer los mensajes de confirmación
    # antes de que la pantalla se borre al volver al menú principal.
    if choice in ['1', '2']:
        await blocking_input("Presione Enter para continuar...")