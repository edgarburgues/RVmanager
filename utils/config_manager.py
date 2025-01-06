import json
import os

class ConfigManager:
    """
    Reads, updates, and writes configuration data to a JSON file.
    """
    def __init__(self, config_file="game_paths.json"):
        """
        Initializes config data and loads from file if present.
        """
        self.config_file = os.path.normpath(config_file)
        self.data = {"game_folders": []}
        self.load_config()

    def load_config(self):
        """
        Loads JSON data from the config file if it exists.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.data = json.load(f)

    def save_config(self):
        """
        Saves the current configuration to the JSON file.
        """
        with open(self.config_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_game_folders(self):
        """
        Returns the configured list of game folders.
        """
        return [
            {"path": os.path.normpath(folder["path"]), "type": folder["type"]}
            for folder in self.data.get("game_folders", [])
        ]

    def add_game_folder(self, folder, console_type):
        """
        Adds a new folder to the configuration if not already present.
        """
        normalized_folder = os.path.normpath(folder)
        if not any(f["path"] == normalized_folder for f in self.data["game_folders"]):
            self.data["game_folders"].append({"path": normalized_folder, "type": console_type})
