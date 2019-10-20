# -*- coding: utf-8 -*-

import tkinter as tk

# Todo : display list of used licences, grouped by licenses or users
# Todo :  + get list of avaiable licences -> need reader of lexLm config file (WIP)
# Todo :  + get list of users -> need binding to Window User (TBD)
# Todo :  + get list of used licences -> need bindings to FlexLm server API (TBD)
# Todo :  + aggregate all lists (TBD)
# Todo :  + display aggregated list -> In form of a tree? (TBD)
from eb_lic_manager.gui.licenses_in_use.data_provider import AbstractDataProvider
from eb_lic_manager.gui.licenses_in_use.licences_in_use import LicensesInUseGUI


class MainGUI(tk.Frame):
    def __init__(self, context, master=None):
        super().__init__(master)
        self.context = context

        self.context.set_licences_in_use_provider(DummyDataProvider())

        self.create_widgets()

    def create_widgets(self):
        self.liu = LicensesInUseGUI(self.context.licences_in_use_provider, self)
        self.liu.grid(row=1, column=0)
        self.pack()

    def get_window(self):
        return self.win


class Context(object):
    def __init__(self):
        self.licences_in_use_provider = None

    def set_licences_in_use_provider(self, provider: AbstractDataProvider):
        self.licences_in_use_provider = provider


class DummyDataProvider(AbstractDataProvider):
    def get_data(self):
        return "Data line 1\nData line 2"

    def add_data_change_listener(self, listener):
        super().add_data_change_listener(listener)
        listener()

    def remove_data_change_listener(self, listener):
        super().remove_data_change_listener(listener)


if __name__ == '__main__':
    context = Context()
    context.data_provider = DummyDataProvider()

    root = tk.Tk()
    root.title("EB Licenses Manager")
    app = MainGUI(context, root)
    app.mainloop()
