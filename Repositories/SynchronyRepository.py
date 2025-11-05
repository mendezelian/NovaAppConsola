import json
# Importa la biblioteca httpx, necesaria para realizar peticiones HTTP asíncronas (async/await)
import httpx
# Importa el gestor de configuración para obtener URLs y credenciales
from ConfigManager import ConfigManager

# Define la clase SynchronyRepository.
# Su responsabilidad es manejar toda la comunicación (peticiones) con una API externa.
class SynchronyRepository:
    
    # Constructor de la clase
    def __init__(self):
        # Carga una instancia del gestor de configuración
        self.config = ConfigManager()
        # Obtiene la URL base de la API desde la configuración
        self.URL_API = self.config.get_api_url()
        # Inicializa el cliente HTTP; se creará cuando se necesite
        self.CLIENT = None
        # Inicializa el token de autenticación; se obtendrá al autenticarse
        self.TOKEN = None

    # Método asíncrono para autenticarse contra la API
    async def authenticate(self):
        """Autenticación automática con email y password."""
        
        # Obtiene el email y la contraseña desde el gestor de configuración
        email = self.config.get_email()
        password = self.config.get_password()
        
        # Comprueba si las credenciales están presentes
        if not email or not password:
            raise RuntimeError("Email o contraseña no configurados.")

        # Crea un cliente httpx temporal solo para la autenticación
        async with httpx.AsyncClient() as client:
            # Realiza la petición POST (asíncrona) al endpoint /login
            response = await client.post(
                f"{self.URL_API}/login",
                # Envía el email y password en el cuerpo de la petición como JSON
                json={"username": email, "password": password}
            )
            # Lanza un error si la respuesta HTTP no fue exitosa (ej. 401, 404, 500)
            response.raise_for_status()
            # Convierte la respuesta JSON en un diccionario de Python
            data = response.json()
            # Almacena el token obtenido en la variable de la instancia (self.TOKEN)
            self.TOKEN = data.get("token")
            
            # Valida que la respuesta realmente contenía un token
            if not self.TOKEN:
                raise RuntimeError("No se recibió token de autenticación.")

    # Método privado asíncrono para preparar el cliente HTTP
    async def _get_client_and_url(self):
        # Vuelve a cargar la URL de la API para asegurar que esté actualizada
        self.URL_API = self.config.get_api_url()
        if not self.URL_API:
            raise ConnectionError("Error: La URL de la API no está configurada.")

        # Comprueba si ya tenemos un token. Si no, llama al método authenticate().
        if not self.TOKEN:
            await self.authenticate()

        # Prepara las cabeceras (headers) que se usarán en todas las peticiones
        # Incluye el token de autorización (Bearer Token)
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        
        # Configura tiempos de espera (timeouts)
        # 10 segundos para conectar, 30 segundos para leer la respuesta completa
        timeout = httpx.Timeout(10.0, read=30.0)
        
        # Crea la instancia del cliente asíncrono (self.CLIENT) con los timeouts y cabeceras
        self.CLIENT = httpx.AsyncClient(timeout=timeout, headers=headers)

        # Devuelve el cliente listo para usar y la URL de la API
        return self.CLIENT, self.URL_API

    # Método asíncrono para obtener todos los clientes
    async def get_all_clients(self):
        try:
            # Prepara el cliente (se autentica si es necesario)
            self.CLIENT, url = await self._get_client_and_url()
            # Realiza la petición GET al endpoint /clientes
            response = await self.CLIENT.get(f"{url}/clientes")
            # Asegura que la respuesta se interprete como UTF-8 (para tildes, etc.)
            response.encoding = 'utf-8'
            # Cierra la conexión del cliente
            await self.CLIENT.aclose()
            # Devuelve los datos de la respuesta decodificados desde JSON
            return response.json()
        
        # Captura errores específicos de httpx (problemas de red, DNS, timeout)
        except httpx.RequestError as e:
            raise RuntimeError(f"Error en la solicitud de clientes: {type(e).__name__} en {e.request.url}") from e
        # Captura errores si la respuesta de la API no es un JSON válido
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error al recibir la respuesta, No es un JSON: {type(e).__name__}") from e

    # Método asíncrono para obtener los clientes destacados
    async def get_featured_clients(self):
        try:
            # Prepara el cliente
            self.CLIENT, url = await self._get_client_and_url()
            # Realiza la petición GET al endpoint /clientes/destacados
            response = await self.CLIENT.get(f"{url}/clientes/destacados")
            response.encoding = 'utf-8'
            await self.CLIENT.aclose()
            return response.json()
        
        # Manejo de errores (idéntico al método anterior)
        except httpx.RequestError as e:
            raise RuntimeError(f"Error en la solicitud de clientes destacados: {type(e).__name__} en {e.request.url}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error al recibir la respuesta, No es un JSON: {type(e).__name__}") from e

    # Método asíncrono para obtener todos los contactos
    async def get_all_contacts(self):
        try:
            # Prepara el cliente
            self.CLIENT, url = await self._get_client_and_url()
            # Realiza la petición GET al endpoint /contactos
            response = await self.CLIENT.get(f"{url}/contactos")
            response.encoding = 'utf-8'
            await self.CLIENT.aclose()
            return response.json()
        
        # Manejo de errores (idéntico al método anterior)
        except httpx.RequestError as e:
            raise RuntimeError(f"Error en la solicitud de contactos: {type(e).__name__} en {e.request.url}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error al recibir la respuesta, No es un JSON: {type(e).__name__}") from e