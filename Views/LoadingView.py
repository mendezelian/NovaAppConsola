import os
import asyncio

# --- Función de Utilidad ---

# Método para limpiar la pantalla de la consola
def clear():
    # 'os.system' ejecuta un comando en la terminal.
    # 'os.name == "nt"' comprueba si el sistema operativo es Windows (NT).
    # Si es Windows, usa el comando "cls".
    # Si es otro (como Linux o macOS), usa el comando "clear".
    os.system("cls" if os.name == "nt" else "clear")

# --- Clase de Vista de Carga ---

# Define una clase para mostrar una animación de carga asíncrona en la consola.
class LoadingView:
    
    # Constructor de la clase
    def __init__(self, frames=None, delay=0.3):
        # Define los 'frames' (cuadros) de la animación.
        # Si el usuario no proporciona 'frames', usa una lista por defecto.
        self.frames = frames or ["Cargandoº..", "Cargando.º.", "Cargando..º"]
        
        # Define el tiempo (en segundos) de espera entre cada frame.
        self.delay = delay
        
        # Crea un 'Evento' de asyncio. Es una bandera para comunicarnos
        # con la tarea de animación y decirle cuándo debe parar.
        self._stop_event = asyncio.Event()
        
        # Una variable para guardar la referencia a la tarea (el bucle) de animación.
        self._task = None

    # Método privado asíncrono que ejecuta el bucle de la animación
    async def _run(self):
        i = 0 # Inicializa un contador para saber qué frame mostrar
        
        # Bucle principal: se ejecuta mientras el evento '_stop_event' NO esté activado.
        while not self._stop_event.is_set():
            # 1. Limpia la consola
            clear()
            
            # 2. Imprime el frame actual.
            # 'i % len(self.frames)' asegura que el índice vuelva a 0
            # cuando llegue al final de la lista (ej. 0, 1, 2, 0, 1, 2, ...)
            print(self.frames[i % len(self.frames)])
            
            # 3. Pausa asíncrona. Esto es clave:
            # 'await asyncio.sleep' detiene ESTA tarea por 'self.delay' segundos,
            # pero permite que otras tareas (como la sincronización de datos)
            # sigan ejecutándose en segundo plano.
            await asyncio.sleep(self.delay)
            
            # 4. Avanza al siguiente frame
            i += 1

    # Método público para iniciar la animación
    async def start(self):
        # Limpia (resetea) la bandera del evento por si se había usado antes.
        self._stop_event.clear()
        
        # 'asyncio.create_task' agenda la corutina '_run' para que se
        # ejecute "en segundo plano" (concurrentemente) en el bucle de eventos.
        # Guardamos la referencia a esta tarea.
        self._task = asyncio.create_task(self._run())

    # Método público para detener la animación
    async def stop(self):
        # Activa la bandera del evento. El bucle 'while' en '_run'
        # verá que 'is_set()' es True y se detendrá.
        self._stop_event.set()
        
        # Comprueba si la tarea existe (si se llamó a 'start')
        if self._task:
            # 'await self._task' espera a que la tarea '_run' termine
            # limpiamente antes de continuar.
            await self._task