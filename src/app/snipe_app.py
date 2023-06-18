import tkinter as tk
from typing import Optional

import customtkinter as ctk

from src.api.lol_client import ClientApi


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

        self.listbox = tk.Listbox(self, width=100, height=20)
        self.listbox.pack()

        self.snipe_button = ctk.CTkButton(self, text="Snipe", command=self.snipe)
        self.snipe_button.pack(pady=10)

        self.update_friends()

    def update_friends(self):
        new_friends = self.api.get_online_friends()

        # Store current listbox values and selected index.
        current_friends = self.listbox.get(0, tk.END)
        current_selection = self.listbox.curselection()

        # If any friend is in ARAM queue, move them to the top.
        for friend in new_friends:
            if friend['lol']['gameQueueType'] == 'ARAM_UNRANKED_5x5':
                new_friends.remove(friend)
                new_friends.insert(0, friend)

        # Update the listbox
        for i, friend in enumerate(new_friends):
            new_status = f"{friend['name']} - {friend['lol']['gameQueueType']} {friend['lol']['gameStatus']}"

            if i < len(current_friends):  # If the entry already exists
                if current_friends[i] != new_status:  # If the entry has changed
                    self.listbox.delete(i)
                    self.listbox.insert(i, new_status)
            else:  # If the entry does not exist
                self.listbox.insert(tk.END, new_status)

        # Remove any trailing entries
        if len(new_friends) < len(current_friends):
            for i in range(len(new_friends), len(current_friends)):
                self.listbox.delete(i)
        # Restore the selected index
        if current_selection:
            current_friends = self.listbox.get(0, tk.END)
            for i, friend in enumerate(current_friends):
                friend_name, _ = friend.split(" - ")
                if friend_name == self.friend_to_snipe:
                    self.listbox.selection_set(i)

        # Check if the friend to snipe is in ARAM queue
        if self.friend_to_snipe:
            current_flow = self.api.get_flow()
            friend = next((friend for friend in new_friends if friend['name'] == self.friend_to_snipe), None)
            if friend and friend['lol']['gameStatus'] == 'inQueue' and current_flow != "Matchmaking":
                if not self.api.in_aram_lobby():
                    self.api.create_aram_lobby()
                    print("Created ARAM lobby")
                self.api.start_queue()
            elif friend and  friend['lol']['gameStatus'] != 'inQueue' and current_flow == "Matchmaking":
                self.api.stop_queue()
                self.api.quit_lobby()
                print("Stopped queue")


        # Update listbox every 0.5 seconds
        self.after(500, self.update_friends)

    def snipe(self):
        # Get selected friend
        selection = self.listbox.curselection()
        friend_to_snipe , _ = self.listbox.get(selection[0]).split(" - ")
        if selection and friend_to_snipe != self.friend_to_snipe:
            self.friend_to_snipe = friend_to_snipe
            self.snipe_button.configure(text="Sniping " + self.friend_to_snipe + "...")

        else:
            self.friend_to_snipe = None
            self.snipe_button.configure(text="Snipe")
