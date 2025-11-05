import json
import os

# Define la clase ConfigManager, responsable de leer y escribir
# el archivo de configuración 'config.json'.
class ConfigManager:
    # Constante: Nombre del archivo de configuración.
    CONFIG_FILE = "config.json"
    
    # Constante: Un diccionario con los valores por defecto.
    # Se usa si 'config.json' no existe o está dañado.
    DEFAULT_CONFIG = {
        "api_url": "https://apitechsolutions.duckdns.org/api",
        "ping": "apitechsolutions.duckdns.org",
        "download_interval_minutes": 5
        # Nota: 'username' y 'password' no están aquí;
        # si no existen, sus 'get' devolverán None.
    }

    # Constructor de la clase
    def __init__(self):
        # Llama al método privado '_load_config' al crear una instancia
        # y almacena el resultado (un diccionario) en 'self._config'.
        self._config = self._load_config()

    # Método privado: Carga la configuración desde el archivo.
    def _load_config(self):
        # 1. Comprobar si el archivo existe.
        if not os.path.exists(self.CONFIG_FILE):
            # Si no existe, guarda el diccionario por defecto y lo devuelve.
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        
        # 2. Si el archivo existe, intentar leerlo.
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                # Carga el JSON del archivo en un diccionario Python.
                config_data = json.load(f)
                
            # 3. Asegurarse de que todas las claves por defecto existen.
            #    Esto es útil si la aplicación se actualiza y añade nuevas claves.
            for key, value in self.DEFAULT_CONFIG.items():
                if key not in config_data:
                    # Si falta una clave, la añade con su valor por defecto.
                    config_data[key] = value
            
            # Vuelve a guardar el archivo (por si faltaba alguna clave).
            self._save_config(config_data)
            return config_data
            
        # 4. Si el archivo está corrupto (no es un JSON válido).
        except json.JSONDecodeError:
            print(f"Advertencia: {self.CONFIG_FILE} corrupto. Restaurando valores.")
            # Sobrescribe el archivo corrupto con los valores por defecto.
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

    # Método privado: Guarda un diccionario en el archivo 'config.json'.
    def _save_config(self, config_data):
        # Abre el archivo en modo escritura ('w').
        with open(self.CONFIG_FILE, 'w') as f:
            # Escribe el 'config_data' en el archivo 'f'.
            # 'indent=2' formatea el JSON para que sea legible.
            json.dump(config_data, f, indent=2)

    # --- Métodos Públicos (Getters) ---
    # Los getters recargan la configuración ('_load_config') cada vez que
    # se llaman. Esto asegura que si el archivo se edita manualmente,
    # la aplicación leerá los valores más recientes.

    def get_api_url(self):
        self._config = self._load_config()
        # Devuelve el valor. Si la clave no existe por alguna razón,
        # usa el valor por defecto como respaldo.
        return self._config.get("api_url", self.DEFAULT_CONFIG["api_url"])

    def get_ping(self):
        self._config = self._load_config()
        # Nota: 'ping' no está en DEFAULT_CONFIG, así que usa 'ping'.
        # Esto podría ser un error o una lógica intencional.
        return self._config.get("ping", self.DEFAULT_CONFIG["ping"])

    def get_download_interval(self):
        self._config = self._load_config()
        return self._config.get("download_interval_minutes", self.DEFAULT_CONFIG["download_interval_minutes"])

    def get_email(self):
        # No recarga, usa la configuración en memoria.
        # Devolverá 'None' si "username" no existe en el config.
        return self._config.get("username")

    def get_password(self):
        # No recarga, usa la configuración en memoria.
        # Devolverá 'None' si "password" no existe en el config.
        return self._config.get("password")

    # --- Métos Públicos (Setters) ---
    # Los setters actualizan el valor en 'self._config' y
    # luego llaman a '_save_config' para persistir el cambio en el disco.

    def set_api_url(self, new_url):
        self._config["api_url"] = new_url
        self._save_config(self._config)
        print(f"URL de API actualizada a: {new_url}")
    
    def set_ping(self, new_ping):
        self._config["ping"] = new_ping
        self._save_config(self._config)
        print(f"HOST de API actualizado a: {new_ping}")
          
    def set_download_interval(self, minutes):
        try:
            # Intenta convertir la entrada (que puede ser un string) a un entero.
            minutes_int = int(minutes)
            
            # Valida que el número sea positivo.
            if minutes_int <= 0:
                print("El intervalo debe ser un número positivo.")
                return # No guarda el cambio
                
            # Actualiza el diccionario y guarda el archivo.
            self._config["download_interval_minutes"] = minutes_int
            self._save_config(self._config)
            print(f"Intervalo de descarga actualizado a: {minutes_int} minutos.")
            
        # Se activa si 'int(minutes)' falla (ej. si la entrada es "abc").
        except ValueError:
            print("Entrada no válida. Debe ser un número entero.")

    # --- Método de Visualización ---
    
    def get_config_display(self):
        # Recarga la configuración para asegurar que muestra los datos más frescos.
        self._config = self._load_config()
        # Devuelve una cadena de texto (string) del JSON formateado.
        return json.dumps(self._config, indent=2)