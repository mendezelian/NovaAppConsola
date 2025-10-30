import requests
import os
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("API_URL")

#Probar conexión
#res = requests.get(URL)
#Consultar clientes

response = requests.get(f"{URL}/clientes")
print(response.text)