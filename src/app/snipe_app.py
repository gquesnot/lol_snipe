import tkinter as tk
from typing import Optional, Dict

import customtkinter as ctk
from src.api.lol_client import ClientApi


class Select:
    def __init__(self, parent, width, height):
        self.listbox = tk.Listbox(parent, width=width, height=height)
        self.listbox.pack()
        self.options: Dict[str, str] = {}

    def update_options(self, new_options: Dict[str, str]):
        # Remove options not present in new_options
        for name in list(self.options.keys()):
            if name not in new_options:
                index = list(self.options.keys()).index(name)
                self.listbox.delete(index)
                del self.options[name]

        # Update existing options and add new options
        for name, status in new_options.items():
            if name in self.options:
                if self.options[name] != status:
                    index = list(self.options.keys()).index(name)
                    self.listbox.delete(index)
                    self.listbox.insert(index, f"{name} - {status}")
                    self.options[name] = status
            else:
                self.listbox.insert(tk.END, f"{name} - {status}")
                self.options[name] = status

    def get_selection(self):
        selection = self.listbox.curselection()
        if selection:
            return list(self.options.keys())[selection[0]]
        return None

    def set_selection(self, name):
        if name in self.options:
            index = list(self.options.keys()).index(name)
            self.listbox.selection_set(index)


class SnipeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snipe")
        self.geometry("500x500")
        self.resizable(False, False)
        self.api = ClientApi()
        self.api.init_api()
        self.friend_to_snipe: Optional[str] = None

        self.label = ctk.CTkLabel(self, text="Online Friends:")
        self.label.pack()

        self.select = Select(self, width=100, height=20)

        self.snipe_button = ctk.CTkButton(self, text="Snipe", command=self.snipe)
        self.snipe_button.pack(pady=10)

        self.update_friends()

    def update_friends(self):
        new_friends = self.api.get_online_friends()
        new_options = {}

        for friend in new_friends:
            if 'lol' in friend and 'gameQueueType' in friend['lol']:
                new_options[friend['name']] = f"{friend['lol']['gameQueueType']} {friend['lol']['gameStatus']}"

        self.select.update_options(new_options)

        if self.friend_to_snipe:
            self.snipe_procedure(new_options)

        # Update listbox every 0.5 seconds
        self.after(500, self.update_friends)

    def snipe_procedure(self, new_options):
        current_flow = self.api.get_flow()
        friend_status = new_options.get(self.friend_to_snipe)

        if friend_status and 'inQueue' in friend_status and current_flow != "Matchmaking" and 'ARAM_UNRANKED_5x5' in friend_status:
            if not self.api.in_aram_lobby():
                self.api.create_aram_lobby()
                print("Created ARAM lobby")
            self.api.start_queue()

        elif friend_status and 'inQueue' not in friend_status and current_flow == "Matchmaking":
            self.api.stop_queue()
            self.api.quit_lobby()
            print("Stopped queue")

    def snipe(self):
        friend_to_snipe = self.select.get_selection()
        if friend_to_snipe and friend_to_snipe != self.friend_to_snipe:
            self.friend_to_snipe = friend_to_snipe
            self.snipe_button.configure(text="Sniping " + self.friend_to_snipe + "...")
        else:
            self.friend_to_snipe = None
            self.snipe_button.configure(text="Snipe")