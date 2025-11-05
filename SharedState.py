# SharedState.py

# --- Nota sobre Concurrencia ---
# No se necesitan locks (candados) porque asyncio
# se ejecuta en un solo hilo.
# La gestión de concurrencia de asyncio (event loop)
# evita que 'set_files' y 'get_files' se ejecuten
# exactamente al mismo tiempo y corrompan los datos.

# Define una clase para almacenar el estado compartido de la aplicación.
class AppState:
    
    # Constructor de la clase
    def __init__(self):
        # Inicializa una variable interna (privada)
        # para guardar la lista de archivos de la base de datos ('db').
        self._db_files = []

    def set_files(self, new_files):
        """Actualiza la lista de archivos."""
        # Este método es un 'setter'.
        # Reemplaza la lista antigua de archivos por la 'new_files' proporcionada.
        self._db_files = new_files

    def get_files(self):
        """Obtiene la lista de archivos."""
        # Este método es un 'getter'.
        # Devuelve una COPIA de la lista de archivos.
        # '.copy()' es importante para evitar que el código
        # que llama a esta función modifique accidentalmente la
        # lista original en 'self._db_files'.
        return self._db_files.copy()

# --- Instancia Global ---
# Se crea una instancia única (Singleton) de la clase AppState.
# Otros módulos de la aplicación (como las Vistas o las Tareas)
# importarán 'global_state' para acceder y modificar
# la lista de archivos de forma centralizada.
global_state = AppState()