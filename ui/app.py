import os
import shutil
from ttkbootstrap import Frame, Button, Treeview, Progressbar, Combobox, Label, Canvas, Text
from tkinter import filedialog, messagebox
from utils.config_manager import ConfigManager
from utils.cover_manager import CoverManager
from utils.game_finder import GameFinder
from utils.usb_utils import USBUtils


class RVLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RVLoader Game Manager")

        self.config_manager = ConfigManager()
        self.cover_manager = CoverManager()

        self.local_games = []
        self.usb_games = []
        self.usb_drive = None

        self.setup_ui()

    def setup_ui(self):
        # ----- Menú de acciones -----
        menu_frame = Frame(self.root, padding=10, bootstyle="primary")
        menu_frame.pack(fill="x")

        Button(
            menu_frame,
            text="Añadir Carpeta (Gamecube)",
            bootstyle="outline-primary",
            command=lambda: self.add_folder("Gamecube")
        ).pack(side="left", padx=5)

        Button(
            menu_frame,
            text="Añadir Carpeta (Wii)",
            bootstyle="outline-primary",
            command=lambda: self.add_folder("Wii")
        ).pack(side="left", padx=5)

        Button(
            menu_frame,
            text="Actualizar Listas",
            bootstyle="outline-success",
            command=self.refresh_game_list
        ).pack(side="left", padx=5)

        # ----- Selección de unidad USB -----
        usb_frame = Frame(self.root, padding=10)
        usb_frame.pack(fill="x")

        Label(usb_frame, text="Unidad USB:").pack(side="left", padx=5)
        self.usb_drive_selector = Combobox(
            usb_frame,
            values=USBUtils.get_available_drives(),
            state="readonly",
            width=30
        )
        self.usb_drive_selector.pack(side="left", padx=5)
        self.usb_drive_selector.bind("<<ComboboxSelected>>", self.load_usb_games)

        # ----- Marco principal con 4 columnas -----
        main_frame = Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Columna 1: Detalles del juego local seleccionado
        local_details_frame = Frame(main_frame, padding=10)
        local_details_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.local_cover_canvas = Canvas(local_details_frame, width=160, height=224, bg="white")
        self.local_cover_canvas.pack()

        self.local_details_text = Text(local_details_frame, width=30, height=10, state="disabled", wrap="word")
        self.local_details_text.pack(pady=5)

        # Columna 2: Lista de juegos locales
        local_list_frame = Frame(main_frame, padding=10)
        local_list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        Label(local_list_frame, text="Juegos Locales", bootstyle="primary").pack(pady=5)

        self.local_games_tree = Treeview(
            local_list_frame,
            columns=("ID", "Name", "Type"),
            show="headings",
            height=20
        )
        self.local_games_tree.heading("ID", text="ID")
        self.local_games_tree.heading("Name", text="Nombre")
        self.local_games_tree.heading("Type", text="Tipo")

        self.local_games_tree.column("ID", width=80, anchor="center")
        self.local_games_tree.column("Name", width=300, anchor="w", stretch=True)
        self.local_games_tree.column("Type", width=100, anchor="center")

        self.local_games_tree.pack(fill="both", expand=True)
        self.local_games_tree.bind("<<TreeviewSelect>>", self.display_local_details)

        # Columna 3: Lista de juegos en USB
        usb_list_frame = Frame(main_frame, padding=10)
        usb_list_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        Label(usb_list_frame, text="Juegos en USB", bootstyle="primary").pack(pady=5)

        self.usb_games_tree = Treeview(
            usb_list_frame,
            columns=("ID", "Name", "Type"),
            show="headings",
            height=20
        )
        self.usb_games_tree.heading("ID", text="ID")
        self.usb_games_tree.heading("Name", text="Nombre")
        self.usb_games_tree.heading("Type", text="Tipo")

        self.usb_games_tree.column("ID", width=80, anchor="center")
        self.usb_games_tree.column("Name", width=300, anchor="w", stretch=True)
        self.usb_games_tree.column("Type", width=100, anchor="center")

        self.usb_games_tree.pack(fill="both", expand=True)
        self.usb_games_tree.bind("<<TreeviewSelect>>", self.display_usb_details)

        # Columna 4: Detalles del juego en USB seleccionado
        usb_details_frame = Frame(main_frame, padding=10)
        usb_details_frame.grid(row=0, column=3, sticky="nsew", padx=10, pady=10)

        self.usb_cover_canvas = Canvas(usb_details_frame, width=160, height=224, bg="white")
        self.usb_cover_canvas.pack()

        self.usb_details_text = Text(usb_details_frame, width=30, height=10, state="disabled", wrap="word")
        self.usb_details_text.pack(pady=5)

        # Ajuste de las proporciones de las columnas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=2)
        main_frame.columnconfigure(3, weight=1)

        # ----- Barra de progreso -----
        progress_frame = Frame(self.root, padding=10)
        progress_frame.pack(fill="x")

        self.progress = Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=10)

        # ----- Botones de acción -----
        actions_frame = Frame(self.root, padding=10)
        actions_frame.pack(fill="x")

        Button(
            actions_frame,
            text="Copiar Juegos al USB",
            bootstyle="outline-danger",
            command=self.copy_games_to_usb
        ).pack(side="left", padx=5)

        Button(
            actions_frame,
            text="Guardar Configuración",
            bootstyle="outline-info",
            command=self.save_config
        ).pack(side="left", padx=5)

        # ----- Carga inicial de la lista de juegos -----
        self.refresh_game_list()

    def add_folder(self, console_type):
        """
        Agrega una carpeta al archivo de configuración (Wii o Gamecube).
        """
        folder = filedialog.askdirectory()
        if folder:
            self.config_manager.add_game_folder(folder, console_type)
            self.refresh_game_list()

    def refresh_game_list(self):
        """
        Refresca la lista de juegos locales leyendo las carpetas configuradas.
        """
        self.local_games_tree.delete(*self.local_games_tree.get_children())
        self.local_games = GameFinder.find_games(self.config_manager.get_game_folders())
        for game in self.local_games:
            self.local_games_tree.insert("", "end", values=(game["id"], game["name"], game["type"]))

    def load_usb_games(self, event):
        """
        Carga la lista de juegos detectados en la unidad USB seleccionada.
        """
        self.usb_games_tree.delete(*self.usb_games_tree.get_children())
        self.usb_drive = self.usb_drive_selector.get()
        if not self.usb_drive:
            return

        self.usb_games = GameFinder.find_games([{"path": self.usb_drive, "type": "Unknown"}])
        for game in self.usb_games:
            self.usb_games_tree.insert("", "end", values=(game["id"], game["name"], game["type"]))

    def save_config(self):
        """
        Guarda la configuración (carpetas de juegos) en el archivo JSON.
        """
        self.config_manager.save_config()
        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")

    def copy_games_to_usb(self):
        """
        Copia los juegos seleccionados en la lista local hacia la unidad USB elegida.
        """
        if not self.usb_drive:
            messagebox.showerror("Error", "Seleccione una unidad USB.")
            return

        selected_items = self.local_games_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione uno o más juegos para copiar.")
            return

        usb_path = self.usb_drive
        selected_games = [self.local_games[int(item)] for item in selected_items]

        self.progress["maximum"] = len(selected_games)
        results = []

        for i, game in enumerate(selected_games):
            result = USBUtils.copy_game_to_usb(game, usb_path)
            results.append(result)
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.progress["value"] = 0
        messagebox.showinfo("Resultados de la copia", "\n".join(results))
        self.load_usb_games(None)  # Refresca la lista de juegos en la unidad USB

    def display_local_details(self, event):
        """
        Muestra detalles y portada del juego local seleccionado.
        """
        self.display_details(
            tree=self.local_games_tree,
            canvas=self.local_cover_canvas,
            details_text=self.local_details_text,
            games=self.local_games
        )

    def display_usb_details(self, event):
        """
        Muestra detalles y portada del juego en USB seleccionado.
        """
        self.display_details(
            tree=self.usb_games_tree,
            canvas=self.usb_cover_canvas,
            details_text=self.usb_details_text,
            games=self.usb_games
        )

    def display_details(self, tree, canvas, details_text, games):
        """
        Función genérica para mostrar los detalles de cualquier juego (local o USB).
        """
        selected_item = tree.selection()
        if not selected_item:
            return

        item_id = selected_item[0]
        item_index = tree.index(item_id)
        game = games[item_index]

        # Descargar y mostrar la portada
        cover_path = self.cover_manager.download_cover(game["id"])
        if cover_path:
            cover_image = self.cover_manager.load_cover_image(cover_path)
            canvas.create_image(0, 0, anchor="nw", image=cover_image)
            canvas.image = cover_image
        else:
            canvas.delete("all")

        # Mostrar texto con la info del juego
        details_text.config(state="normal")
        details_text.delete(1.0, "end")
        details_text.insert("end", f"Nombre: {game['name']}\n")
        details_text.insert("end", f"ID: {game['id']}\n")
        details_text.insert("end", f"Tipo: {game['type']}\n")
        details_text.insert("end", f"Ruta: {game['path']}\n")
        details_text.config(state="disabled")
