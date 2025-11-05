# Define la función 'list_contacts_view'.
# Esta función pertenece a la capa de "Vista" (View).
# Su única responsabilidad es tomar una lista de datos y mostrársela al usuario.
# Recibe un argumento: 'contacts' (se espera que sea una lista de objetos ContactModel).
def list_contacts_view(contacts):
    
    # Comprueba si la lista 'contacts' está vacía o es 'None'.
    if not contacts:
        # Si no hay nada que mostrar, imprime un mensaje informativo.
        print("No hay contactos para mostrar.")
        # Proporciona una pista al usuario sobre cómo obtener los datos.
        print("Asegúrate de 'Sincronizar Datos' (Opción 2) primero.")
        # Detiene la ejecución de la función.
        return
    
    # Si la lista tiene contenido, imprime un encabezado.
    print("--- Lista de Contactos (de 'contacts.json') ---")
    
    # Inicia un bucle para iterar sobre cada objeto 'contact' en la lista 'contacts'.
    for contact in contacts:
        
        # Convierte el valor booleano (True/False) de 'contact.get_is_client'
        # en una cadena de texto legible para el usuario ("Sí" o "No").
        # (Esto se llama operador ternario).
        client_status = "Sí" if contact.get_is_client else "No"
        
        # Imprime los detalles formateados de este contacto específico.
        # (Nota: Asume que .get_id, .get_name, etc., son propiedades
        # del objeto 'contact', no métodos que necesiten '()').
        print(f"ID: {contact.get_id}")
        print(f" 	Nombre: {contact.get_name}")
        print(f" 	Email: {contact.get_email}")
        print(f" 	Es Cliente: {client_status}")
        
        # Imprime una línea separadora para distinguir este contacto del siguiente.
        print("-" * 20)