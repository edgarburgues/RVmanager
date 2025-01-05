import json
import os

class ConfigManager:
    """
    Se encarga de leer y escribir el archivo de configuración (por defecto: game_paths.json).
    """
    def __init__(self, config_file="game_paths.json"):
        self.config_file = os.path.normpath(config_file)
        self.data = {"game_folders": []}
        self.load_config()

    def load_config(self):
        """
        Carga la configuración desde el archivo JSON si existe.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.data = json.load(f)

    def save_config(self):
        """
        Guarda la configuración en el archivo JSON.
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_game_folders(self):
        """
        Retorna la lista de carpetas de juegos, normalizando las rutas.
        """
        return [
            {"path": os.path.normpath(folder["path"]), "type": folder["type"]}
            for folder in self.data.get("game_folders", [])
        ]

    def add_game_folder(self, folder, console_type):
        """
        Agrega una carpeta de juegos con su tipo (Wii o Gamecube) si no existe ya.
        """
        normalized_folder = os.path.normpath(folder)
        if not any(f["path"] == normalized_folder for f in self.data["game_folders"]):
            self.data["game_folders"].append({"path": normalized_folder, "type": console_type})
