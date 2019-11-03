# -*- coding: utf-8 -*-
import datetime
import tkinter as tk

# Todo : display list of used licences, grouped by licenses or users
# Todo :  + get list of avaiable licences -> need reader of lexLm config file (WIP)
# Todo :  + get list of users -> need binding to Window User (TBD)
# Todo :  + get list of used licences -> need bindings to FlexLm server API (TBD)
# Todo :  + aggregate all lists (TBD)
# Todo :  + display aggregated list -> In form of a tree? (TBD)
from eb_lic_manager.gui.context import Context, LicencesProvider, UsersProvider
from eb_lic_manager.gui.licenses_in_use.data_provider import AbstractDataProvider
from eb_lic_manager.gui.licenses_in_use.licences_in_use import LicensesInUseGUI, LicencesInUse


class MainGUI(tk.Frame):
    def __init__(self, context, master=None):
        super().__init__(master)
        self.context = context

        self.create_widgets()

    def create_widgets(self):
        self.liu = LicensesInUseGUI(self.context.licences_in_use, self)
        self.liu.grid(row=1, column=0)
        self.pack()

    def get_window(self):
        return self.win


class DummyDataProvider(AbstractDataProvider):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

    def get_data(self):
        liu_holder = LicencesInUse(self.context)
        liu_holder.clear()
        for lic in ["lic1", "lic2", "lic3"]:
            for user in ["user1", "user2", "user3"]:
                liu_holder.add(lic, user, datetime.datetime.now())

        return liu_holder


if __name__ == '__main__':
    context = Context()
    context.set_licences_in_use_provider(DummyDataProvider(context))
    context.set_licenses_provider(LicencesProvider())
    context.set_users_provider(UsersProvider())

    root = tk.Tk()
    root.title("EB Licenses Manager")
    app = MainGUI(context, root)
    app.mainloop()
