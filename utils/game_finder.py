import os

class GameFinder:
    @staticmethod
    def find_games(folders, extensions=('.iso', '.wbfs')):
        """
        Searches for games in .iso or .wbfs format within the specified folders.
        Returns a list of dictionaries with each game's information.
        """
        games = []
        for folder in folders:
            folder_path = os.path.normpath(folder["path"])
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(extensions):
                        game_path = os.path.normpath(os.path.join(root, file))
                        console_type = GameFinder.get_console_type(folders, root, file)
                        games.append(GameFinder.extract_game_info(game_path, console_type))
        return games

    @staticmethod
    def extract_game_info(game_path, console_type):
        """
        Extracts the ID and name of a game from the ISO/WBFS file.
        """
        title_id = GameFinder.get_title_id(game_path)
        game_name = GameFinder.get_game_name(game_path)
        return {"id": title_id, "name": game_name, "path": game_path, "type": console_type}

    @staticmethod
    def get_title_id(game_path):
        """
        Reads the first 6 bytes (different offset for .iso or .wbfs) to get the ID.
        """
        with open(game_path, 'rb') as f:
            offset = 0x0 if game_path.endswith('.iso') else 0x200
            f.seek(offset)
            return f.read(6).decode('ascii')

    @staticmethod
    def get_game_name(game_path):
        """
        Reads 64 bytes (different offset for .iso or .wbfs) to get the name.
        """
        with open(game_path, 'rb') as f:
            offset = 0x20 if game_path.endswith('.iso') else 0x220
            f.seek(offset)
            return f.read(64).decode('ascii', errors='ignore').strip('\x00').strip()

    @staticmethod
    def get_console_type(folders, root, file):
        """
        Determines if a .wbfs file is Wii, or uses the folder path
        to infer whether it's Wii or Gamecube.
        """
        if file.endswith('.wbfs'):
            return "Wii"
        
        for folder in folders:
            if os.path.normpath(root).startswith(os.path.normpath(folder["path"])):
                return folder["type"]

        return "Unknown"
