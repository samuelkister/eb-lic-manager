import abc


class AbstractDataProvider(abc.ABC):
    def __init__(self):
        self.listeners = []

    @abc.abstractmethod
    def add_data_change_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)
            listener()

    @abc.abstractmethod
    def remove_data_change_listener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def notify_all(self):
        for listener in self.listeners:
            listener()

    @abc.abstractmethod
    def get_data(self):
        return "Not implemented"

