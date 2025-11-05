# Controllers/SynchronyController.py

# Importa la clase de servicio que contiene la lógica de sincronización
from Services.SynchronyService import SynchronyService

# Define la clase SynchronyController
# Su propósito es recibir la orden de "sincronizar" y pasarla al servicio.
class SynchronyController:
    
    # Constructor de la clase
    def __init__(self):
        # Crea una instancia del servicio de sincronización (SynchronyService)
        # Este servicio es el que realmente hará el trabajo.
        self.synchronyService = SynchronyService()
    
    # Método principal para iniciar el proceso de sincronización
    def synchronize(self):

        # Inicia un bloque try para manejar los errores que puedan ocurrir
        # durante todo el proceso de sincronización.
        try:
            # Llama al método 'run_process' del servicio.
            # Esta es la función que orquesta la ejecución de los subprocesos.
            return self.synchronyService.run_process()
        
        # Captura errores de conexión (ej. si la URL de la API no está configurada)
        except ConnectionError as e:
            print(f"{e}")
            
        # Captura errores de tiempo de ejecución (ej. si falla un subproceso o la API)
        except RuntimeError as e:
            print(f"{e}")
            
        # Captura cualquier otro error genérico que no se haya previsto
        except Exception as e:
            print(f"Error inespetado: {e}")