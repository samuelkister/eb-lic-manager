# -*- coding: utf-8 -*-
import datetime
import tkinter as tk
from collections import namedtuple
from itertools import groupby
from operator import attrgetter
from tkinter import ttk
from eb_lic_manager.gui.licenses_in_use.data_provider import AbstractDataProvider


# ToDo : GOAL -> Display the licences in use in a tree, grouped by Licence or user
# ToDo : Make a window class to hold the tree
# ToDo : Get and display the list of licences in use

UsedTuple = namedtuple('UsedTuple', 'license, user, since')


class LicensesInUseGUI(tk.Frame):
    def new_data(self):
        self.data: LicencesInUse = self.data_provider.get_data()
        self.display_data()

    def __init__(self, data_provider: AbstractDataProvider, master=None):
        """

        :type data_provider: provider of the data to display
        """
        super().__init__(master)
        self.master = master
        self.create_widgets()
        self.data = None
        self.data_provider = data_provider
        self.data_provider.add_data_change_listener(self.new_data)

    def create_widgets(self):
        # Button to group by License or User
        self.btnGroupBy = ttk.Button(self, text='Group by User')
        self.btnGroupBy.grid(column=0, row=1)
        self.btnGroupBy.pack(side=tk.TOP)

        self.tree = ttk.Treeview(self)
        self.tree.pack(side=tk.BOTTOM)

        # self.pack()

    def display_data(self):
        txt = []
        # ToDo: extract the right inormation for level 1 and level 2 object (grouped by licence or user...)
        for lv1_object, lv1_iterator in self.data.get_licenses_in_use():
            parent = self.tree.insert(text=lv1_object.id, parent='', index='end')
            txt.append(lv1_object.id)
            for lv2_object in lv1_iterator:
                self.tree.insert(text=lv2_object.user.id, parent=parent, index='end')
                txt.append("             {}".format(lv2_object.user.id))
        # self.tree["text"] = "\n".join(txt)


class LicencesInUse(object):
    """
    Holder class for the licences in use.
    Makes the link between the licences in use and the user that uses them
    Can return them grouped by licences or by user
    """

    BY_LICENSE = 0
    BY_USER = 1

    def __init__(self, context):
        self._context = context
        self._licences_in_use = None
        self.clear_licences_in_use()

    def clear_licences_in_use(self):
        self._licences_in_use = []

    def add_license_user(self, license_id: str, user_id: str, since: datetime.datetime):
        self._licences_in_use.append(UsedTuple(
            self._context.licenses.get_data(license_id),
            self._context.users.get_data(user_id),
            since))

    def get_licenses_in_use(self, by=BY_LICENSE):
        # ToDo : finish function : group by "by"
        keyfunc = attrgetter('license' if (by == self.BY_LICENSE) else 'user')
        src = sorted(self._licences_in_use, key=keyfunc)

        return groupby(src, key=keyfunc)


