from consolemenu import *
from consolemenu.items import *

from ..foundation.command.Command import Command


class SettingsCommand(Command):
    __slots__ = ['menu']

    def __init__(self):
        Command.__init__(self)

        menu = ConsoleMenu("Kathara Settings", "Choose the option to change")

        # MenuItem is the base class for all items, it doesn't do anything when selected
        menu_item = MenuItem("Menu Item")

        def resetNetworkCounter():
            print("Network Counter Resetted!")

        # A FunctionItem runs a Python function when selected
        function_item = FunctionItem("Reset the network counter", resetNetworkCounter)

        # A SelectionMenu constructs a menu from a list of strings
        selection_menu = SelectionMenu(["Quagga", "Frr", "OpenVSwitch", "P4"])

        # A SubmenuItem lets you add a menu (the selection_menu above, for example)
        # as a submenu of another menu
        submenu_item = SubmenuItem("Choose default image", selection_menu, menu)

        deployer_menu = SelectionMenu(["Kathara (Docker)", "Megalos (Kubernetes)"])

        # A SubmenuItem lets you add a menu (the selection_menu above, for example)
        # as a submenu of another menu
        deployer_item = SubmenuItem("Choose default adapter", deployer_menu, menu)

        menu.append_item(menu_item)
        menu.append_item(function_item)
        menu.append_item(submenu_item)
        menu.append_item(deployer_item)

        self.menu = menu

    def run(self, current_path, argv):
        self.menu.show()
