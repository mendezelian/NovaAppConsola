import httpx
from dotenv import load_dotenv
import os
import asyncio

#Cargar variables de entorno
load_dotenv()

#URL de la API
URL = os.getenv("API_URL")

#Crear el cliente para hacer peticiones asíncronas con httpx
client = httpx.AsyncClient()

# obtener todos los clientes
async def getAllClients():
    response = await client.get(f"{URL}/clientes")
    await client.aclose()
    return response
#Obtener los clientes destacados
async def getFeaturedClients():
     response = await client.get(f"{URL}/clientes/destacados")
     await client.aclose()
     print(response.text)
     return response

#obtener todos los contactos
async def getAllContacts():
    response = await client.get(f"{URL}/contactos")
    await client.aclose()
    return response
    
#obtener ventas del mes
async def getNumSalesMonth():
    response = await client.get(f"{URL}/ventas")
    await client.aclose()
    return response

#obtener total de ventas
async def getTotalSales():
    response = await client.get(f"{URL}/ventas/total")
    return response

#obtener pendientes de envío
async def getPendingOrders():
    response = await client.get(f"{URL}/ventas/pendientes")
    print(response.text)
    
#Obtener productos con stock bajo
async def getProductsLowStock():
    response = await client.get(f"{URL}/ventas/stockbajo")
    await client.aclose()
    print(response.text)
    return response

asyncio.run(getProductsLowStock())