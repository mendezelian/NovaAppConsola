# Importa las bibliotecas de asyncio (para tareas asíncronas) y time (para medir el tiempo)
import asyncio, time

# Define una función 'async' (una corutina).
# Esta función actúa como un "envoltorio" (wrapper) para mostrar un mensaje de carga
# mientras ejecuta otra función que es 'bloqueante' (síncrona).
async def is_loading(task_function):
    
    # Imprime el estado inicial "Cargando...".
    # 'end=""' evita que se imprima un salto de línea.
    # 'flush=True' fuerza a la consola a mostrar el texto inmediatamente.
    print("Cargando...", end="", flush=True)
    
    # Obtiene el bucle de eventos de asyncio actual.
    loop = asyncio.get_event_loop()
    
    # Registra el tiempo de inicio para calcular la duración.
    start = time.time()
    
    # Inicia un bloque para capturar cualquier error que ocurra en la tarea.
    try:
        # --- Punto Clave ---
        # 'loop.run_in_executor' ejecuta la 'task_function' (que es bloqueante)
        # en un hilo separado (usando el ejecutor por defecto 'None').
        # 'await' pausa la función 'is_loading' aquí, pero NO bloquea el bucle de asyncio,
        # permitiendo que otras tareas (como una UI) sigan funcionando.
        result = await loop.run_in_executor(None, task_function)
        
        # Una vez que la tarea en el hilo termina:
        # '\r' (Retorno de Carro) mueve el cursor al inicio de la línea.
        # Esto sobrescribe el "Cargando..." original con el mensaje de éxito.
        # Se calcula y formatea el tiempo transcurrido (ej. "1.23s").
        print(f"\rCargando... ¡Hecho! ({time.time() - start:.2f}s)")
        
        # Devuelve el resultado de 'task_function'. Si 'result' es None o False,
        # devuelve "Finalizado." como valor por defecto.
        return result or "Finalizado."
    
    # Si la 'task_function' lanzó una excepción, se captura aquí.
    except Exception as e:
        # Sobrescribe el "Cargando..." con un mensaje de error.
        print(f"\rCargando... ¡Falló! ({time.time() - start:.2f}s)")
        
        # Devuelve un mensaje de error formateado.
        return f"Error: {e}"