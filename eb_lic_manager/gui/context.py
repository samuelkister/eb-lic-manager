from eb_lic_manager.gui.licenses_in_use.data_provider import AbstractDataProvider


class Context(object):
    def __init__(self):
        self.licences_in_use: AbstractDataProvider = None
        self.licenses: AbstractDataProvider = None
        self.users: AbstractDataProvider = None

    def set_licences_in_use_provider(self, provider: AbstractDataProvider):
        self.licences_in_use = provider

    def set_users_provider(self, user_provider: AbstractDataProvider):
        self.users = user_provider

    def set_licenses_provider(self, licenses_provider: AbstractDataProvider):
        self.licenses = licenses_provider


class License(object):
    def __init__(self, id=None, name="Not created"):
        self.id = id
        self.name = name

    def __lt__(self, other):
        return  self.id < other.id


class LicencesProvider(AbstractDataProvider):

    def __init__(self):
        super().__init__()
        self._new_license = License()
        self._licenses: dict = {}
        self.clear()

    def get_data(self, id=None):
        if id:
            found = self._licenses.setdefault(id, self._new_license)

            if found.id != id:
                found.id = id
                self._new_license = License()

            return found

        else:
            return self._licenses.values()

    def clear(self):
        self._licenses.clear()


class User(object):
    def __init__(self, id=None, name="Not created"):
        self.id = id
        self.name = name

    def __lt__(self, other):
        return  self.id < other.id


class UsersProvider(AbstractDataProvider):

    def __init__(self):
        super().__init__()
        self._new_user = User()
        self._users: dict = {}
        self.clear()

    def get_data(self, id=None):
        if id:
            found = self._users.setdefault(id, self._new_user)

            if found.id != id:
                found.id = id
                self._new_user = User()

            return found

        else:
            return self._users.values()

    def clear(self):
        self._users.clear()
