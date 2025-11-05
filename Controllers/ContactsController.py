# Importa la clase ContactsService desde el módulo Services
from Services.ContactsService import ContactsService

# Define la clase ContactsController.
# Esta clase gestiona las solicitudes (entradas) y las dirige al servicio correspondiente.
class ContactsController:
    
    # Constructor de la clase
    def __init__(self):
        # Crea una instancia de ContactsService y la almacena en self.contactService.
        # El controlador usará este servicio para realizar las operaciones de lógica de negocio.
        self.contactService = ContactsService()
    
    # Método para obtener todos los contactos
    def get_all_contacts(self):
        # Inicia un bloque 'try' para manejar los errores que puedan ocurrir.
        try:
            # Llama al método get_all_contacts() del servicio para obtener los datos.
            contacts = self.contactService.get_all_contacts()
            # Si la llamada es exitosa, devuelve la lista de contactos.
            return contacts
        
        # Captura específicamente los errores de tipo RuntimeError.
        # Estos son los errores que hemos estado lanzando desde las capas inferiores (Servicio y Repositorio).
        except RuntimeError as e:
            # Imprime un mensaje de error indicando que es un error controlado ("Error de flujo").
            print(f"Error de flujo: {e}")
            
        # Captura cualquier otro tipo de error genérico (Exception) que no sea RuntimeError.
        except Exception as e:
            # Imprime un mensaje indicando que fue un error no esperado.
            print(f"Error inesperado: {e}")