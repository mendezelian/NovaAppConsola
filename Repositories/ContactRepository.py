# Define la clase ContactRepository, que agrupa métodos para acceder a datos de contacto.
class ContactRepository:
    
    # Este es el constructor de la clase. Se llama cuando se crea un objeto de esta clase.
    def __init__(self):
        # Establece la ruta base (el directorio) donde se guardan los archivos JSON.
        self.PATH_DB = "db"
        
    # Método para obtener todos los clientes
    def get_all_clients(self):
        # 'try' inicia un bloque para manejar posibles errores que ocurran al leer el archivo.
        try:
            # 'with open' abre el archivo y asegura que se cierre automáticamente.
            # f"{self.PATH_DB}\\clients.json" construye la ruta al archivo.
            # 'r' indica modo lectura, 'encoding='utf-8'' asegura compatibilidad de caracteres.
            with open(f"{self.PATH_DB}\\clients.json", 'r', encoding='utf-8') as f:
                # Lee todo el contenido del archivo (f.read()) y lo devuelve como una cadena (str).
                return str(f.read())
        
        # Captura el error específico si la ruta es un directorio, no un archivo.
        except IsADirectoryError as e:
            # Lanza (raise) un nuevo error de tipo RuntimeError, incluyendo el mensaje original (e).
            raise RuntimeError(f"Error la ruta es un directorio: {e}") from e
        
        # Captura el error si el archivo no se encuentra en la ruta especificada.
        except FileNotFoundError as e:
            raise RuntimeError(f"Error el archivo no existe en la ruta: {e}") from e
        
        # Captura otros errores generales de Entrada/Salida (I/O), como problemas de permisos.
        except IOError as e:
            raise RuntimeError(f"Error al leer el fichero {e}") from e
            
    # Método para obtener los clientes destacados
    def get_featured_clients(self):
        # Inicia el bloque de manejo de errores para este método.
        try:
            # Abre el archivo específico de clientes destacados.
            with open(f"{self.PATH_DB}\\featured_clients.json", 'r', encoding='utf-8') as f:
                # Lee y devuelve el contenido como cadena.
                return str(f.read())
        
        # Manejo de errores (idéntico al método anterior, pero para este archivo).
        except IsADirectoryError as e:
            raise RuntimeError(f"Error la ruta es un directorio: {e}") from e
        except FileNotFoundError as e:
            raise RuntimeError(f"Error el archivo no existe en la ruta: {e}") from e
        except IOError as e:
            raise RuntimeError(f"Error al leer el fichero {e}") from e

    # Método para obtener todos los contactos
    def get_all_contacts(self):
        # Inicia el bloque de manejo de errores.
        try:
            # Abre el archivo 'contacts.json'.
            with open(f"{self.PATH_DB}\\contacts.json", 'r', encoding='utf-8') as f:
                # Lee y devuelve el contenido como cadena.
                return str(f.read())
        
        # Manejo de errores (idéntico a los métodos anteriores, pero para 'contacts.json').
        except IsADirectoryError as e:
            raise RuntimeError(f"Error la ruta es un directorio: {e}") from e
        except FileNotFoundError as e:
            raise RuntimeError(f"Error el archivo no existe en la ruta: {e}") from e
        except IOError as e:
            raise RuntimeError(f"Error al leer el fichero {e}") from e