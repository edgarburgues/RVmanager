import json
import os

class ConfigManager:
    """
    Handles reading and writing the configuration file (defaults to game_paths.json).
    """
    def __init__(self, config_file="game_paths.json"):
        self.config_file = os.path.normpath(config_file)
        self.data = {"game_folders": []}
        self.load_config()

    def load_config(self):
        """
        Loads the configuration from the JSON file if it exists.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.data = json.load(f)

    def save_config(self):
        """
        Saves the configuration to the JSON file.
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_game_folders(self):
        """
        Returns the list of game folders, normalizing the paths.
        """
        return [
            {"path": os.path.normpath(folder["path"]), "type": folder["type"]}
            for folder in self.data.get("game_folders", [])
        ]

    def add_game_folder(self, folder, console_type):
        """
        Adds a game folder with its console type (Wii or Gamecube) if it doesn't already exist.
        """
        normalized_folder = os.path.normpath(folder)
        if not any(f["path"] == normalized_folder for f in self.data["game_folders"]):
            self.data["game_folders"].append({"path": normalized_folder, "type": console_type})
