class ContactModel :
    #Constructor del Modelo
    def __init__(self,id=None,name="UNKNOW",email="UNKNOW",is_client=False):
        self._id = id
        self._name = name
        self._email = email
        self._is_client = is_client
        
    #Getter del id
    @property
    def get_id(self):
        return self._id
    #Getter del nombre
    @property
    def get_name(self):
        return self._name
    #Setter del nombre
    @get_name.setter
    def set_name(self,name):
        self._name = name
    #Getter del Email
    @property
    def get_email(self):
        return self._email
    #Setter del Email
    @get_email.setter
    def set_email(self,email):
        self._email = email
    #Getter del estado del contacto
    @property
    def get_is_client(self):
        return self._is_client
    #Setter del estado del contacto
    @get_is_client.setter
    def set_is_client(self,is_client):
        self._is_client = is_client
        