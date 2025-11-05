# Services/SynchronyService.py
import json
import asyncio
import os
from datetime import datetime
# Importa el repositorio que se comunica con la API
from Repositories.SynchronyRepository import SynchronyRepository
# Importa Process y Pipe para ejecutar tareas en paralelo (en diferentes procesos)
from multiprocessing import Process, Pipe
from ConfigManager import ConfigManager

# Define la clase SynchronyService, que orquesta la sincronización de datos.
class SynchronyService:
    
    # Constructor de la clase
    def __init__(self):
        # Instancia el repositorio para acceder a los métodos de la API
        self.synchronyRepository = SynchronyRepository()
        _config = ConfigManager()
        # Define la ruta del directorio donde se guardarán los archivos JSON
        self.DB_PATH = "db"
        # Define la ruta del archivo de log
        self.LOGS = "logs/logs.log"
        # Obtiene el host (aunque no se usa en este fragmento, es parte de la config)
        self.HOST = _config.get_ping()
        # Crea el directorio 'db' si no existe. 'exist_ok=True' evita un error si ya existe.
        os.makedirs(self.DB_PATH, exist_ok=True)
    
    # --- Métodos de Tarea (Diseñados para Procesos Hijos) ---
    # Cada uno de estos métodos (clients, contacts, featured_clients) está
    # diseñado para ser ejecutado en un Proceso separado.
    # Reciben un argumento 'conn' (una conexión de Tubería/Pipe) para devolver el resultado.

    def clients(self, conn):
        try:
            # Crea un nuevo bucle de eventos asyncio (necesario para ejecutar 'async' en un nuevo proceso).
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Ejecuta la tarea asíncrona del repositorio (la llamada a la API)
            result = loop.run_until_complete(self.synchronyRepository.get_all_clients())
            # Envía el resultado (los datos) de vuelta al proceso padre
            conn.send(result)
        except Exception as e:
            # Si algo falla, envía un diccionario de error de vuelta
            conn.send({"Error": f"{type(e).__name__}: {e}"})
        finally:
            # Cierra la conexión del pipe, sea cual sea el resultado
            conn.close()

    def contacts(self, conn):
        try:
            # Lógica idéntica a 'clients', pero para el endpoint de contactos
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.synchronyRepository.get_all_contacts())
            conn.send(result)
        except Exception as e:
            conn.send({"Error": f"{type(e).__name__}: {e}"})
        finally:
            conn.close()

    def featured_clients(self, conn):
        try:
            # Lógica idéntica a 'clients', pero para el endpoint de clientes destacados
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.synchronyRepository.get_featured_clients())
            conn.send(result)
        except Exception as e:
            conn.send({"Error": f"{e}"})
        finally:
            conn.close()

    # Método para crear/sobrescribir un archivo JSON
    def create_json(self, name, data):
        # Construye la ruta completa al archivo (ej: "db/clients.json")
        filepath = os.path.join(self.DB_PATH, name)
        try:
            # Abre el archivo en modo escritura ('w')
            with open(filepath, 'w', encoding='utf-8') as f:
                # Escribe los 'data' en el archivo 'f' con formato JSON
                # ensure_ascii=False permite guardar tildes y 'ñ' correctamente
                # indent=2 formatea el JSON para que sea legible
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            # Maneja errores si no se puede escribir el archivo
            print(f"Error al escribir el archivo {filepath}: {e}")

    # --- NUEVA FUNCIÓN ---
    def _is_data_new(self, filename, new_data):
        """Compara new_data con el contenido actual de filename."""
        filepath = os.path.join(self.DB_PATH, filename)
        
        # Si el archivo principal no existe, cualquier dato se considera "nuevo"
        if not os.path.exists(filepath):
            return True
            
        try:
            # Intenta leer el archivo JSON existente
            with open(filepath, 'r', encoding='utf-8') as f:
                # Carga y decodifica el JSON del archivo a un objeto Python
                old_data = json.load(f)
            # Compara el objeto antiguo con el objeto nuevo.
            # Devuelve True si son diferentes, False si son iguales.
            return old_data != new_data
        except (json.JSONDecodeError, IOError):
            # Si el archivo viejo está corrupto (mal JSON) o no se puede leer,
            # tratamos los datos nuevos como si fueran nuevos para forzar una re-escritura.
            return True

    # --- FUNCIÓN MODIFICADA (Orquestador Principal) ---
    def run_process(self):
        p1, p2, p3 = None, None, None # Inicializa variables de proceso
        log = None # Inicializa variable de log
        try:
            # Abre el archivo de logs en modo 'append' (añadir al final)
            with open(self.LOGS, "a", encoding="utf-8") as log:
                        
                # --- Configuración de Procesos y Tuberías (Pipes) ---
                # pr1 = extremo padre (recibe), ch1 = extremo hijo (envía)
                pr1, ch1 = Pipe()
                # Define el Proceso 1: ejecutará 'self.clients' y usará 'ch1' para enviar datos
                p1 = Process(target=self.clients, args=(ch1,))
                
                pr2, ch2 = Pipe()
                p2 = Process(target=self.contacts, args=(ch2,))
                
                pr3, ch3 = Pipe()
                p3 = Process(target=self.featured_clients, args=(ch3,))
                
                # --- Ejecución ---
                # Inicia los 3 procesos. Ahora se ejecutan en paralelo.
                p1.start()
                p2.start()
                p3.start()
                
                # --- Recolección de Resultados ---
                # El proceso padre espera (se bloquea) aquí hasta recibir datos de cada hijo
                clients_result = pr1.recv()
                contacts_result = pr2.recv()
                featured_result = pr3.recv()
                
                # Espera a que los procesos hijos terminen completamente
                p1.join()
                p2.join()
                p3.join()
                
                # --- Verificación de Errores ---
                # Agrupa todos los resultados para una fácil comprobación
                all_results = {
                    "clients": clients_result,
                    "contacts": contacts_result,
                    "featured_clients": featured_result
                }
                # Revisa si alguno de los resultados fue un diccionario de error
                for name, result in all_results.items():
                    if isinstance(result, dict) and "Error" in result:
                        # Si un proceso falló, detiene toda la sincronización
                        raise RuntimeError(f"Error en '{name}': {result['Error']}")
                
                # --- LÓGICA DELTA-CHECK (Comprobación de cambios) ---
                # Compara el resultado de la API con el archivo en disco
                is_new_clients = self._is_data_new("clients.json", clients_result)
                is_new_contacts = self._is_data_new("contacts.json", contacts_result)
                is_new_featured = self._is_data_new("featured_clients.json", featured_result)

                # Si NINGUNO de los archivos tiene datos nuevos
                if not (is_new_clients or is_new_contacts or is_new_featured):
                    log.write("No hay datos nuevos. Sincronización omitida.\n")
                    log.flush() # Asegura que se escriba en el log
                    return # Termina la función aquí para no hacer escrituras innecesarias

                # Si llegamos aquí, al menos un archivo tiene datos nuevos
                log.write("Datos nuevos detectados. Guardando archivos...\n")
                log.flush()
                # Genera un timestamp (marca de tiempo) para los archivos de archivo/historial
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                # --- Escritura de Archivos ---
                
                # 1. Sobrescribir los archivos principales (solo si cambiaron)
                if is_new_clients:
                    self.create_json("clients.json", clients_result)
                if is_new_contacts:
                    self.create_json("contacts.json", contacts_result)
                if is_new_featured:
                    self.create_json("featured_clients.json", featured_result)
                
                # 2. Crear los archivos de archivo/historial con timestamp (solo si cambiaron)
                if is_new_clients:
                    self.create_json(f"clients_{timestamp}.json", clients_result)
                if is_new_contacts:
                    self.create_json(f"contacts_{timestamp}.json", contacts_result)
                if is_new_featured:
                    self.create_json(f"featured_clients_{timestamp}.json", featured_result)
                
                log.write(f"Sincronización completada. Archivos guardados con timestamp: {timestamp}\n")
                log.flush()
        
        except Exception as e:
            # --- Manejo de Errores Graves ---
            # Si algo falla en el orquestador principal (ej. un error de Runtime)
            with open(self.LOGS, 'a', encoding='utf-8') as log_error:
                log_error.write(f"Falló la Sincronización: {e}\n")
            
            # Limpieza de procesos: intenta terminar cualquier proceso hijo que
            # pudiera haber quedado colgado (zombie)
            for p in [p1, p2, p3]:
                if p and p.is_alive(): # Si el proceso existe y sigue vivo
                    p.terminate() # Forzar su finalización
                    p.join() # Limpiar el proceso