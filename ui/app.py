import os
import threading
from tkinter import filedialog, messagebox
from ttkbootstrap import Frame, Button, Treeview, Progressbar, Combobox, Label, Canvas, Text
from utils.config_manager import ConfigManager
from utils.cover_manager import CoverManager
from utils.game_finder import GameFinder
from utils.usb_utils import USBUtils

class RVLoaderApp:
    """
    Provides the main GUI for managing local and USB games.
    """
    def __init__(self, root, base_dir):
        self.root = root
        self.base_dir = base_dir
        cfg_file = os.path.join(self.base_dir, "game_paths.json")
        covers_folder = os.path.join(self.base_dir, "assets", "covers")

        self.config_manager = ConfigManager(cfg_file)
        self.cover_manager = CoverManager(covers_folder)

        self.local_games = []
        self.usb_games = []
        self.usb_drive = None

        self.setup_ui()
        self.refresh_game_list()

    def setup_ui(self):
        """
        Builds the layout with:
         - A top frame for folder buttons (left) and USB drive selection (right).
         - A main frame with 5 columns:
             0: Local details
             1: Local list
             2: '>>' copy button centered
             3: USB list
             4: USB details + Delete button
         - A bottom frame for progress bar and 'Save Configuration'.
        """
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        top_frame = Frame(self.root, padding=5)
        top_frame.grid(row=0, column=0, sticky="nsew")

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        left_top_frame = Frame(top_frame)
        right_top_frame = Frame(top_frame)
        left_top_frame.grid(row=0, column=0, sticky="w")
        right_top_frame.grid(row=0, column=1, sticky="e")

        Button(left_top_frame, text="Add Folder (Gamecube)", bootstyle="outline-primary", command=lambda: self.add_folder("Gamecube")).pack(side="left", padx=5)
        Button(left_top_frame, text="Add Folder (Wii)", bootstyle="outline-primary", command=lambda: self.add_folder("Wii")).pack(side="left", padx=5)
        Button(left_top_frame, text="Refresh Lists", bootstyle="outline-success", command=self.refresh_game_list).pack(side="left", padx=5)

        Label(right_top_frame, text="USB Drive:").pack(side="left", padx=5)
        self.usb_drive_selector = Combobox(right_top_frame, values=USBUtils.get_available_drives(), state="readonly", width=25)
        self.usb_drive_selector.pack(side="left", padx=5)
        self.usb_drive_selector.bind("<<ComboboxSelected>>", self.load_usb_games)

        main_frame = Frame(self.root, padding=5)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=0)
        main_frame.columnconfigure(3, weight=2)
        main_frame.columnconfigure(4, weight=1)
        main_frame.rowconfigure(0, weight=1)

        local_details_frame = Frame(main_frame)
        local_details_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.local_cover_canvas = Canvas(local_details_frame, width=160, height=224, bg="white")
        self.local_cover_canvas.pack()

        self.local_details_text = Text(local_details_frame, width=35, height=10, state="disabled", wrap="word")
        self.local_details_text.pack(pady=5)

        local_list_frame = Frame(main_frame)
        local_list_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        Label(local_list_frame, text="Local Games").pack(pady=5)

        self.local_games_tree = Treeview(local_list_frame, columns=("ID", "Name", "Type"), show="headings", height=20)
        self.local_games_tree.heading("ID", text="ID")
        self.local_games_tree.heading("Name", text="Name")
        self.local_games_tree.heading("Type", text="Type")
        self.local_games_tree.column("ID", width=80, anchor="center")
        self.local_games_tree.column("Name", width=220, anchor="w", stretch=True)
        self.local_games_tree.column("Type", width=80, anchor="center")
        self.local_games_tree.pack(fill="both", expand=True)
        self.local_games_tree.bind("<<TreeviewSelect>>", self.display_local_details)

        copy_frame = Frame(main_frame)
        copy_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        copy_frame.rowconfigure(0, weight=1)
        copy_frame.rowconfigure(1, weight=0)
        copy_frame.rowconfigure(2, weight=1)

        copy_button = Button(copy_frame, text=">>", bootstyle="outline-danger", command=self.copy_games_to_usb)
        copy_button.grid(row=1, column=0)

        usb_list_frame = Frame(main_frame)
        usb_list_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)

        Label(usb_list_frame, text="USB Games").pack(pady=5)

        self.usb_games_tree = Treeview(usb_list_frame, columns=("ID", "Name", "Type"), show="headings", height=20)
        self.usb_games_tree.heading("ID", text="ID")
        self.usb_games_tree.heading("Name", text="Name")
        self.usb_games_tree.heading("Type", text="Type")
        self.usb_games_tree.column("ID", width=80, anchor="center")
        self.usb_games_tree.column("Name", width=220, anchor="w", stretch=True)
        self.usb_games_tree.column("Type", width=80, anchor="center")
        self.usb_games_tree.pack(fill="both", expand=True)
        self.usb_games_tree.bind("<<TreeviewSelect>>", self.display_usb_details)

        usb_details_frame = Frame(main_frame)
        usb_details_frame.grid(row=0, column=4, sticky="nsew", padx=5, pady=5)
        usb_details_frame.rowconfigure(0, weight=1)
        usb_details_frame.rowconfigure(1, weight=0)

        details_container = Frame(usb_details_frame)
        details_container.grid(row=0, column=0, sticky="nsew")

        self.usb_cover_canvas = Canvas(details_container, width=160, height=224, bg="white")
        self.usb_cover_canvas.pack()

        self.usb_details_text = Text(details_container, width=35, height=10, state="disabled", wrap="word")
        self.usb_details_text.pack(pady=5)

        delete_button_frame = Frame(usb_details_frame)
        delete_button_frame.grid(row=1, column=0, sticky="ew", pady=5)

        Button(delete_button_frame, text="Delete from USB", bootstyle="outline-danger", command=self.delete_game_from_usb).pack()

        bottom_frame = Frame(self.root, padding=5)
        bottom_frame.grid(row=2, column=0, sticky="nsew")

        self.progress = Progressbar(bottom_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=5, side="left", expand=True)

        Button(bottom_frame, text="Save Configuration", bootstyle="outline-info", command=self.save_config).pack(side="right", padx=5)

    def add_folder(self, console_type):
        """
        Opens a directory dialog to add a new folder of a specified console type.
        """
        folder = filedialog.askdirectory()
        if folder:
            self.config_manager.add_game_folder(folder, console_type)
            self.refresh_game_list()

    def refresh_game_list(self):
        """
        Clears and repopulates the local games list from config folders.
        """
        self.local_games_tree.delete(*self.local_games_tree.get_children())
        self.local_games = GameFinder.find_games(self.config_manager.get_game_folders())
        for i, game in enumerate(self.local_games):
            self.local_games_tree.insert("", "end", iid=str(i), values=(game["id"], game["name"], game["type"]))

    def load_usb_games(self, event):
        """
        Detects and lists games on the selected USB drive.
        """
        self.usb_games_tree.delete(*self.usb_games_tree.get_children())
        self.usb_drive = self.usb_drive_selector.get()
        if not self.usb_drive:
            return
        found = GameFinder.find_games([{"path": self.usb_drive, "type": "Unknown"}])
        self.usb_games = found
        for i, game in enumerate(self.usb_games):
            self.usb_games_tree.insert("", "end", iid=str(i), values=(game["id"], game["name"], game["type"]))

    def save_config(self):
        """
        Saves the current configuration to the config file.
        """
        self.config_manager.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully.")

    def copy_games_to_usb(self):
        """
        Copies selected local games to the USB drive using a background thread.
        """
        if not self.usb_drive:
            messagebox.showerror("Error", "Select a USB drive.")
            return
        selected_items = self.local_games_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Select one or more games to copy.")
            return
        usb_path = self.usb_drive
        selected_games = [self.local_games[int(item)] for item in selected_items]
        self.progress["maximum"] = len(selected_games)
        self.progress["value"] = 0
        thread = threading.Thread(target=self._copy_games_in_background, args=(selected_games, usb_path))
        thread.start()

    def _copy_games_in_background(self, selected_games, usb_path):
        """
        Copies games in a separate thread to avoid UI freeze.
        """
        results = []
        total = len(selected_games)
        for i, game in enumerate(selected_games):
            result = USBUtils.copy_game_to_usb(game, usb_path)
            results.append(result)
            self.root.after(0, lambda current=i+1: self._update_copy_progress(current, total))
        self.root.after(0, lambda: self._show_copy_results(results))

    def _update_copy_progress(self, current, total):
        """
        Updates the progress bar value.
        """
        self.progress["value"] = current
        if current >= total:
            self.progress["value"] = 0

    def _show_copy_results(self, results):
        """
        Shows a message box with the copy results and refreshes the USB list.
        """
        messagebox.showinfo("Copy Results", "\n".join(results))
        self.load_usb_games(None)

    def delete_game_from_usb(self):
        """
        Deletes selected games from the USB drive.
        """
        if not self.usb_drive:
            messagebox.showerror("Error", "Select a USB drive.")
            return
        selected_items = self.usb_games_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Select one or more games to delete.")
            return
        confirm = messagebox.askyesno("Confirm Deletion", "Do you want to permanently delete the selected games?")
        if not confirm:
            return
        results = []
        for item in selected_items:
            game = self.usb_games[int(item)]
            res = USBUtils.delete_game_from_usb(game, self.usb_drive)
            results.append(res)
        self.load_usb_games(None)
        messagebox.showinfo("Deletion Results", "\n".join(results))

    def display_local_details(self, event):
        """
        Displays details for the selected local game.
        """
        selected_item = self.local_games_tree.selection()
        if not selected_item:
            return
        index = int(selected_item[0])
        game = self.local_games[index]
        cover_path = self.cover_manager.download_cover(game["id"])
        if cover_path:
            cover_image = self.cover_manager.load_cover_image(cover_path)
            self.local_cover_canvas.create_image(0, 0, anchor="nw", image=cover_image)
            self.local_cover_canvas.image = cover_image
        else:
            self.local_cover_canvas.delete("all")
        self.local_details_text.config(state="normal")
        self.local_details_text.delete("1.0", "end")
        self.local_details_text.insert("end", f"Name: {game['name']}\n")
        self.local_details_text.insert("end", f"ID: {game['id']}\n")
        self.local_details_text.insert("end", f"Type: {game['type']}\n")
        self.local_details_text.insert("end", f"Path: {game['path']}\n")
        self.local_details_text.config(state="disabled")

    def display_usb_details(self, event):
        """
        Displays details for the selected USB game.
        """
        selected_item = self.usb_games_tree.selection()
        if not selected_item:
            return
        index = int(selected_item[0])
        game = self.usb_games[index]
        cover_path = self.cover_manager.download_cover(game["id"])
        if cover_path:
            cover_image = self.cover_manager.load_cover_image(cover_path)
            self.usb_cover_canvas.create_image(0, 0, anchor="nw", image=cover_image)
            self.usb_cover_canvas.image = cover_image
        else:
            self.usb_cover_canvas.delete("all")
        self.usb_details_text.config(state="normal")
        self.usb_details_text.delete("1.0", "end")
        self.usb_details_text.insert("end", f"Name: {game['name']}\n")
        self.usb_details_text.insert("end", f"ID: {game['id']}\n")
        self.usb_details_text.insert("end", f"Type: {game['type']}\n")
        self.usb_details_text.insert("end", f"Path: {game['path']}\n")
        self.usb_details_text.config(state="disabled")