import asyncio

# Define una función asíncrona (corutina) para el submenú de gestión de archivos.
# Recibe:
# - clear: La función para limpiar la consola.
# - global_state: Un objeto para acceder al estado (como la lista de archivos).
# - blocking_input: La función asíncrona para pedir datos al usuario.
# - FileManager: Un objeto con métodos BLOQUEANTES para la E/S de archivos.
# - BackgroundTasks: Un objeto para forzar la actualización de tareas en segundo plano.
async def manage_files_menu(clear, global_state, blocking_input, FileManager, BackgroundTasks):
    """Menú para Ver, Añadir, Editar, Eliminar archivos."""
    
    # Obtiene el bucle de eventos de asyncio. Se usará para ejecutar tareas bloqueantes
    # (como abrir un editor) en un hilo separado.
    loop = asyncio.get_event_loop()
    
    # Inicia el bucle principal del menú (se repite hasta que el usuario elija 'q').
    while True:
        # Limpia la pantalla en cada iteración.
        clear()
        print("--- ADMINISTRAR ARCHIVOS ---")
        
        # Obtiene la lista de archivos MÁS RECIENTE desde el objeto de estado global.
        files = global_state.get_files()
        
        # Comprueba si se encontraron archivos.
        if not files:
            print("No se encontraron archivos .json en 'db'.")
        else:
            # Si hay archivos, los lista con un índice numérico (empezando en 1).
            print("Archivos disponibles en 'db':")
            for i, filename in enumerate(files, 1):
                print(f"  {i}. {filename}")
        
        # Muestra las opciones del menú.
        print("\nOpciones:")
        print("  'v [num]' - Ver archivo (ej: v 1)")
        print("  'a'       - Añadir nuevo archivo")
        print("  'e [num]' - Editar archivo (ej: e 2)")
        print("  'd [num]' - Eliminar archivo (ej: d 2)")
        print("  'q'       - Volver al menú principal")
        
        # Espera (await) la entrada del usuario usando la función asíncrona.
        # Esto no bloquea el bucle de eventos principal.
        choice = await blocking_input("Seleccione: ")
        # Limpia y normaliza la entrada (quita espacios, convierte a minúsculas).
        choice = choice.strip().lower()
        
        # Si la opción es 'q' (quit/salir), rompe el bucle 'while True'.
        if choice == 'q':
            break
        
        # --- AÑADIR (a) ---
        if choice == 'a':
            # Pide el nombre del nuevo archivo (asíncrono).
            new_filename = await blocking_input("Nombre del nuevo archivo (ej: mi_archivo.json): ")
            
            # Si el usuario proporcionó un nombre...
            if new_filename:
                # Ejecuta la función BLOQUEANTE 'add_db_file' (que abre un editor)
                # en un hilo separado para no congelar la aplicación.
                await loop.run_in_executor(None, FileManager.add_db_file, new_filename)
                
                # Fuerza al vigilante de archivos a recargar la lista
                # para que el nuevo archivo aparezca inmediatamente.
                await BackgroundTasks.run_file_watcher(force_update=True)
            
            # Pausa (bloqueante) para que el usuario vea el resultado.
            input("Presione Enter para continuar...")
            # 'continue' salta al inicio del 'while True'
            continue

        # --- MANEJO DE COMANDOS CON ARGUMENTOS (v, e, d) ---
        try:
            # Divide la entrada (ej. "v 1" -> ["v", "1"])
            parts = choice.split()
            
            # Valida que el formato sea correcto (acción + número)
            if len(parts) != 2:
                print("Formato incorrecto. Use 'v 1' o 'e 1'.")
                await asyncio.sleep(1) # Pausa breve para ver el error
                continue # Vuelve al inicio del bucle
            
            action = parts[0] # La acción (v, e, d)
            # Convierte el número (string) a índice (int).
            # Resta 1 porque la lista se muestra desde 1, pero los índices empiezan en 0.
            file_index = int(parts[1]) - 1
            
            # Valida que el índice esté dentro de los límites de la lista de archivos.
            if not (0 <= file_index < len(files)):
                print("Número de archivo fuera de rango.")
                await asyncio.sleep(1)
                continue
                
            # Obtiene el nombre del archivo seleccionado.
            filename = files[file_index]
            
            # --- VER (v) ---
            if action == 'v':
                clear()
                # 'view_db_file' es síncrona pero rápida (solo imprime).
                # No necesita 'run_in_executor'.
                FileManager.view_db_file(filename)
                await blocking_input("\nPresione Enter para continuar...")
            
            # --- EDITAR (e) ---
            elif action == 'e':
                clear()
                # 'edit_db_file' es BLOQUEANTE (abre un editor externo).
                # Debe ejecutarse en un hilo separado.
                await loop.run_in_executor(None, FileManager.edit_db_file, filename)
                await blocking_input("\nPresione Enter para continuar...")
            
            # --- ELIMINAR (d) ---
            elif action == 'd':
                clear()
                # 'delete_db_file' es BLOQUEANTE (pide confirmación síncrona).
                # Debe ejecutarse en un hilo separado.
                deleted = await loop.run_in_executor(None, FileManager.delete_db_file, filename)
                
                # Si el archivo fue realmente eliminado...
                if deleted:
                    # ...fuerza la recarga de la lista de archivos.
                    await BackgroundTasks.run_file_watcher(force_update=True)
                await blocking_input("\nPresione Enter para continuar...")
            
            # Si la acción no es v, e, o d
            else:
                print("Acción no reconocida.")
                await asyncio.sleep(1)
                
        # Captura el error si 'int(parts[1])' falla (ej. "v abc")
        except ValueError:
            print("Número de archivo no válido.")
            await asyncio.sleep(1)
        # Captura cualquier otro error inesperado
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)