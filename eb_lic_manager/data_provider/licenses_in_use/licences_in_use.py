# -*- coding: utf-8 -*-
import datetime
import tkinter as tk
from collections import namedtuple
from itertools import groupby
from operator import attrgetter
from tkinter import ttk

from eb_lic_manager.application.context import User, License
from eb_lic_manager.data_provider.licenses_in_use import AbstractDataProvider

# ToDo : GOAL -> Display the licences in use in a tree, grouped by Licence or user

"""
Tuple containing the usage information for one licence by one user
"""
UsedTuple = namedtuple('UsedTuple', 'license, user, since')


class LicensesInUseGUI(tk.Frame):
    """
    GTK Frame to display the licences in use.
    Has:
     - A button to define the grouping by user or license
     - A tree view to display the grouped licences usage information
    """

    _BY_LICENSE = 0
    _BY_USER = 1

    def new_data(self):
        """
        Callback for the data provider to inform that new data are available
        """
        self._get_data()
        self._display_data()

    def _get_data(self):
        """
        Retrieve data from the data provider
        """
        self.data = self.data_provider.get_data()
        self.dataValid = True

    def __init__(self, data_provider: AbstractDataProvider, master=None):
        """
        :param data_provider: provider of the licences in use
        :param master: GUI master in which this Frame is inserted
        """
        super().__init__(master)

        self.groupBy = self._BY_LICENSE
        self.dataValid = False

        self.master = master
        self._create_widgets()
        self.data: LicencesInUse = None
        self.data_provider = data_provider
        self.data_provider.add_data_change_listener(self.new_data)

    def _create_widgets(self):
        # Button to group by License or User
        self.btnGroupBy = ttk.Button(self, command=self._btnGroupBy_on_click)
        self._btnGroupBy_set_text()
        self.btnGroupBy.grid(column=0, row=1)
        self.btnGroupBy.pack(side=tk.TOP)

        # Tree to display the licences in use
        self.tree = ttk.Treeview(self)
        self.tree.pack(side=tk.BOTTOM)

    def _display_data(self):
        if not self.dataValid:
            self._get_data()

        for children in self.tree.get_children():
            self.tree.delete(children)

        # ToDo: extract the right information for level 1 and level 2 object (grouped by licence or user...)
        for lv1_object, lv1_iterator in self.data.get_licenses_in_use(by=self.groupBy):
            txt = None
            if self.groupBy == self._BY_USER:
                user:User = lv1_object
                txt = '{} ({})'.format(user.id, user.name)
            else:
                lic:License = lv1_object
                txt = '{} ({})'.format(lic.name, lic.id)

            parent = self.tree.insert(text=txt, parent='', index='end', open=True)

            for lv2_object in lv1_iterator:
                txt = None
                if self.groupBy == self._BY_USER:
                    user: User = lv2_object.user
                    txt = '{} ({}) since {}'.format(user.id, user.name, lv2_object.since)
                else:
                    lic: License = lv2_object.license
                    txt = '{} ({}) since {}'.format(lic.name, lic.id, lv2_object.since)

                self.tree.insert(text=txt, parent=parent, index='end')

    def _btnGroupBy_set_text(self):
        self.btnGroupBy['text'] = 'Group by Licence' if self.groupBy == self._BY_LICENSE else 'Group by User'

    def _btnGroupBy_on_click(self):
        """
        Callback for click event on btnGroupBy
        """
        if self.groupBy == self._BY_LICENSE:
            self.groupBy = self._BY_USER
        else:
            self.groupBy = self._BY_LICENSE

        self._btnGroupBy_set_text()
        self._display_data()

    def _discard_data(self):
        """
        Signal that the actual used data are invalid and should not be used before renewing.
        """
        self.dataValid = False


class LicencesInUse(object):
    """
    Holder class for the licences in use.
    Makes the link between the licences in use and the user that uses them
    Can return them grouped by licences or by user
    """

    BY_LICENSE = 0
    BY_USER = 1

    def __init__(self, context):
        """
        Creator
        :param context: a Context object holding the necessary environment
        """
        self._context = context
        self._licences_in_use = None
        self.clear()

    def clear(self):
        """
        Empty the list of licences in use
        """
        self._licences_in_use = []

    def add(self, license_id: str, user_id: str, since: datetime.datetime):
        """
        Add a licence in use information
        :param license_id: id of the licence to be added
        :param user_id: user using this license
        :param since: datetime since when the licence is in use by this user
        """
        self._licences_in_use.append(UsedTuple(
            self._context.licenses.get_data(license_id),
            self._context.users.get_data(user_id),
            since))

    def get_licenses_in_use(self, by=BY_LICENSE):
        """
        Return a sorted, grouped list of the stored licences in use
        :param by: grouping BY_LICENSE or BY_USER
        :return: Iterator[Tuple[UsedTuple, Iterator[UsedTuple]]]
        """
        keyfunc = attrgetter('license' if (by == self.BY_LICENSE) else 'user')
        src = sorted(self._licences_in_use, key=keyfunc)

        return groupby(src, key=keyfunc)


