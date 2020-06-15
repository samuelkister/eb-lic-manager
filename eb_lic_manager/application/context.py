from eb_lic_manager.data_provider.licenses_in_use import AbstractDataProvider


class Server(object):
    def __init__(self, name: str = None, id: str = None, port: int = None):
        self.name = name
        self.id = id
        self.port = port

    def set_name(self, name: str):
        self.name = name

    def set_id(self, id: str):
        self.id = id

    def set_port(self, port: str):
        self.port = port


class Context(object):
    def __init__(self):
        self.licences_in_use: AbstractDataProvider = None
        self.licenses: AbstractDataProvider = None
        self.users: AbstractDataProvider = None
        self._servers = []

    def set_licences_in_use_provider(self, provider: AbstractDataProvider):
        self.licences_in_use = provider

    def set_users_provider(self, user_provider: AbstractDataProvider):
        self.users = user_provider

    def set_licenses_provider(self, licenses_provider: AbstractDataProvider):
        self.licenses = licenses_provider

    def create_new_server(self) -> Server:
        server = Server()
        self._servers.append(server)

        return server

    def get_servers(self):
        return self._servers


class License(object):
    def __init__(self, licence_id=None, name="Not created"):
        self.id = licence_id
        self.name = name

    def __lt__(self, other):
        return self.id < other.id


class LicencesProvider(AbstractDataProvider):

    def __init__(self):
        super().__init__()
        self._new_license = License()
        self._licenses: dict = {}
        self.clear()

    def get_data(self, license_id=None):
        if license_id:
            found = self._licenses.setdefault(license_id, self._new_license)

            if found.id != license_id:
                found.id = license_id
                self._new_license = License()

            return found

        else:
            return self._licenses.values()

    def clear(self):
        self._licenses.clear()


class User(object):
    def __init__(self, user_id=None, name="Not created"):
        self.id = user_id
        self.name = name

    def __lt__(self, other):
        return  self.id < other.id


class UsersProvider(AbstractDataProvider):

    def __init__(self):
        super().__init__()
        self._new_user = User()
        self._users: dict = {}
        self.clear()

    def get_data(self, user_id=None):
        if user_id:
            found = self._users.setdefault(user_id, self._new_user)

            if found.id != user_id:
                found.id = user_id
                self._new_user = User()

            return found

        else:
            return self._users.values()

    def clear(self):
        self._users.clear()
