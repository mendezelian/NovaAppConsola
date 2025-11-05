# Define una función asíncrona (corutina) para la vista del menú principal.
# Recibe dos funciones como argumentos: 'clear' (para limpiar pantalla)
# y 'blocking_input' (para obtener entrada del usuario de forma asíncrona).
async def MainMenuView(clear, blocking_input):
    
    # 1. Llama a la función 'clear' para limpiar la consola antes de mostrar el menú.
    clear()
    
    # 2. Imprime las líneas que forman la interfaz de texto del menú.
    print("\n" + "=" * 32)
    print("--- MENÚ PRINCIPAL ---")
    print("=" * 32)
    print("1. Listar Contactos")
    print("2. Forzar Sincronización Manual")
    print("3. Administrar Archivos Locales")
    print("4. Configuración")
    print("5. Probar Conexión (Ping API)")
    print("6. Salir")
    print("-" * 32)
    print("Estado: Tareas en segundo plano activas.")
    
    # 3. Inicia un bucle infinito para solicitar la entrada del usuario.
    #    El bucle solo se romperá con un 'return' cuando la entrada sea válida.
    while True:
        # Inicia un bloque 'try' para capturar errores de entrada.
        try:
            # Llama y 'espera' (await) a la función de entrada asíncrona.
            # 'blocking_input' debe ser una corutina que devuelve la entrada como string.
            option_str = await blocking_input("Seleccione una opción (1-6): ")
            
            # Intenta convertir el string recibido en un número entero.
            # Esto lanzará un 'ValueError' si la entrada no es un número (ej. "a").
            option = int(option_str)
            
            # Comprueba si el número está dentro del rango válido (1 a 6).
            if 1 <= option <= 6:
                # Si es válido, devuelve el número de la opción y sale de la función.
                return option
            else:
                # Si el número está fuera de rango (ej. 7), informa al usuario.
                print("Opción no válida. Intente de nuevo.")
                
        # Captura el error si la conversión 'int()' falló.
        except ValueError:
            # Informa al usuario que la entrada debe ser numérica.
            print("Entrada no válida. Debe ser un número.")
            
        # Si el código llega aquí (debido a un 'else' o 'except'),
        # el 'while True' se repetirá, pidiendo la opción de nuevo.