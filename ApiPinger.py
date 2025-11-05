# Importa la biblioteca para hacer peticiones HTTP asíncronas
import httpx
# Importa el gestor de configuración para obtener la URL
from ConfigManager import ConfigManager
# Importa datetime para añadir marcas de tiempo a los logs
from datetime import datetime

# Define una función asíncrona (corutina) para probar la conexión con la API
async def ping_api(mostrar_en_pantalla: bool = False):
    """
    Realiza una petición HEAD a la API para comprobar si está en línea.
    Registra el resultado en un archivo de log y, opcionalmente,
    en la consola.
    """
    
    # Crea una instancia del gestor de configuración
    config_manager = ConfigManager()
    # Obtiene la URL específica para el 'ping' desde la configuración
    url = config_manager.get_ping()
    # Define la ruta del archivo de log
    log_path = "logs/logs.log"

    # Define una función anidada (helper) para centralizar el registro
    def log_message(msg: str):
        # Obtiene la hora actual y la formatea
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        # Crea el mensaje completo con la marca de tiempo
        mensaje = f"{timestamp} {msg}"
        
        # Abre el archivo de log en modo 'append' (añadir al final)
        with open(log_path, "a", encoding="utf-8") as log:
            # Escribe el mensaje en el archivo
            log.write(mensaje + "\n")
        
        # Si la función fue llamada con mostrar_en_pantalla=True...
        if mostrar_en_pantalla:
            # ...también imprime el mensaje en la consola
            print(mensaje)

    # --- Inicio de la lógica del Ping ---

    # Comprueba si la URL se cargó correctamente
    if not url:
        log_message("Error: No se ha configurado la URL de la API.")
        # Termina la función si no hay URL
        return

    # Registra el inicio del intento de ping
    log_message(f"Haciendo ping a {url}...")
    
    # Inicia un bloque try para capturar errores de red o de la API
    try:
        # Crea un cliente HTTP asíncrono con un timeout de 5 segundos
        # 'async with' asegura que el cliente se cierre correctamente
        async with httpx.AsyncClient(timeout=5.0) as client:
            
            # Realiza una petición 'HEAD' (await la hace asíncrona)
            # 'HEAD' es más rápido que 'GET' porque solo pide las cabeceras,
            # no el cuerpo de la respuesta. Es ideal para un ping.
            response = await client.head(url)
            
            # Lanza una excepción si el código de estado es un error (ej. 404, 500)
            response.raise_for_status()
            
        # Si 'raise_for_status()' no dio error, la conexión fue exitosa
        log_message(f"¡Éxito! Código de estado: {response.status_code}. La API está disponible.")
    
    # --- Manejo de Errores Específicos ---
    
    # Captura el error si la conexión tarda más de 5 segundos
    except httpx.ConnectTimeout:
        log_message(f"Error: Timeout. No se pudo conectar a {url}.")
    
    # Captura errores de conexión (ej. el servidor está apagado)
    except httpx.ConnectError:
        log_message(f"Error: Fallo de conexión. ¿Está el servidor corriendo en {url}?")
    
    # Captura errores de estado HTTP (ej. 404 No Encontrado, 401 No Autorizado)
    except httpx.HTTPStatusError as e:
        log_message(f"Error: La API respondió con un error: {e}")
    
    # Captura otros errores generales de la solicitud httpx
    except httpx.RequestError as e:
        log_message(f"Error: Ocurrió un error de solicitud: {type(e).__name__}")
    
    # Captura cualquier otro error inesperado
    except Exception as e:
        log_message(f"Error inesperado: {e}")