# Importa las clases necesarias de otros módulos
from Repositories.ContactRepository import ContactRepository
import json
from Models.ContactModel import ContactModel

# Define la clase ContactsService, que maneja la lógica de negocio para los contactos.
class ContactsService:
    
    # Constructor de la clase
    def __init__(self):
        # Crea una instancia del repositorio para acceder a la capa de datos.
        self._contactsRepository = ContactRepository()
        # Inicializa una variable para mantener un modelo de contacto (parece usarse temporalmente).
        self._contactModel = None
    
    # Método público para obtener todos los contactos
    def get_all_contacts(self):
        # Inicia un bloque de manejo de errores.
        try:
            # 1. Obtiene los datos en formato string JSON desde el repositorio.
            response = self._contactsRepository.get_all_contacts()
            # 2. Convierte (decodifica) el string JSON en un objeto Python (diccionario o lista).
            response = json.loads(response)
            # 3. Transforma los datos crudos de Python en una lista de objetos 'ContactModel'.
            contacts = self._parse_json_in_list_model(response)
        
        # Captura errores si el JSON recibido está mal formado.
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error al decodificar el JSON: {e}") from e
        # Captura errores que puedan venir del repositorio (ej. archivo no encontrado).
        except RuntimeError as e:
            raise RuntimeError(e) from e
        
        # Devuelve la lista de modelos de contacto.
        return contacts
    
    # Método para crear un objeto modelo de contacto
    def create_contact_model(self, id, email, name, is_client):
        # Crea una instancia del modelo 'ContactModel' con los datos proporcionados.
        # También almacena esta instancia en la variable interna '_contactModel'.
        self._contactModel = ContactModel(id, name, email, is_client)
        # Devuelve el objeto modelo recién creado.
        return self._contactModel
    
    # Método privado para verificar si un ID de contacto pertenece a un cliente
    def _contact_is_client(self, id):
        # Inicia el manejo de errores para la consulta de clientes.
        try:
            # 1. Obtiene el string JSON de todos los clientes desde el repositorio.
            clients = self._contactsRepository.get_all_clients()
            # 2. Decodifica el JSON.
            clients = json.loads(clients)
            # 3. Comprueba si 'alguno' (any) de los elementos 'c' en la lista 'clients["Clientes"]'
            #    tiene un 'id' que coincida con el 'id' del contacto.
            return any(c["id"] == id for c in clients["Clientes"])
        
        # Manejo de errores de decodificación JSON.
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error al decodificar el JSON: {e}") from e
        # Manejo de cualquier otro error durante la consulta.
        except Exception as e:
            raise RuntimeError(f"Error al consultar clientes: {e}") from e
            
    # Método privado para transformar el JSON crudo en una lista de modelos
    def _parse_json_in_list_model(self, data):
        # Inicializa una lista vacía para almacenar los objetos modelo.
        contacts = list()
        
        try:
            # Itera sobre cada diccionario de contacto en la lista 'data["contactos"]'.
            for contacto in data["contactos"]:
                # Extrae los datos de cada contacto.
                id = contacto["id"]
                
                # Limpieza de datos: si el email es 'False' (o nulo), usa "Desconocido".
                email = contacto["email"] if contacto["email"] != False else "Desconocido"
                # Limpieza de datos: si el nombre es 'False', usa "Desconocido".
                name = contacto["name"] if contacto["name"] != False else "Desconocido"
                
                try:
                    # Llama al método interno para verificar si este ID es también un cliente.
                    is_client = self._contact_is_client(id)
                except RuntimeError as e:
                    # Si falla la verificación, lanza un error.
                    raise RuntimeError(f"Error al verificar cliente: {e}") from e
                
                try:
                    # Crea el objeto 'ContactModel' usando el método de esta clase.
                    # Añade el nuevo objeto modelo a la lista 'contacts'.
                    contacts.append(self.create_contact_model(id, email, name, is_client))
                
                # Captura errores si falta una clave (ej. "id") en el diccionario 'contacto'.
                except KeyError as e:
                    raise ValueError(f"Error en la clave del objeto JSON : {e}") from e
                # Captura otros errores durante la creación del modelo.
                except ValueError as e:
                    raise ValueError(f"Error al crear el modelo de contacto : {e}")
            
            # Devuelve la lista completa de objetos modelo.
            return contacts
        
        # Captura un error general si falla la iteración (ej. si 'data["contactos"]' no existe).
        except Exception as e:
            raise RuntimeError(f"Error al iterar contactos : {e}") from e