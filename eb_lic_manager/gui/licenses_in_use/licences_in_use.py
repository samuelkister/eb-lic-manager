# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk


# ToDo : GOAL -> Display the licences in use in a tree, grouped by Licence or user
# ToDo : Make a window class to hold the tree
# ToDo : Get and display the list of licences in use
from eb_lic_manager.gui.licenses_in_use.data_provider import AbstractDataProvider


class LicensesInUseGUI(tk.Frame):
    def new_data(self):
        self.data = self.data_provider.get_data()
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
        self.btnGroupBy = ttk.Button(self, text='Group by User', state=tk.DISABLED)
        self.btnGroupBy.grid(column=0, row=1)
        self.btnGroupBy.pack(side=tk.TOP)

        self.tree = tk.Label(self)
        self.tree.pack(side=tk.BOTTOM)

        # self.pack()

    def display_data(self):
        self.tree["text"] = self.data
