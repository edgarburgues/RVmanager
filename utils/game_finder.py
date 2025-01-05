import os

class GameFinder:
    """
    Searches for .iso and .wbfs files in specified folders and extracts game info.
    """
    @staticmethod
    def find_games(folders, extensions=(".iso", ".wbfs")):
        """
        Scans the provided folders for matching file extensions.
        """
        games = []
        for folder in folders:
            folder_path = os.path.normpath(folder["path"])
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(extensions):
                        game_path = os.path.normpath(os.path.join(root, file))
                        console_type = GameFinder.get_console_type(folder_path, root, file, folder["type"])
                        games.append(GameFinder.extract_game_info(game_path, console_type))
        return games

    @staticmethod
    def extract_game_info(game_path, console_type):
        """
        Reads the title ID and name from the game file.
        """
        title_id = GameFinder.get_title_id(game_path)
        game_name = GameFinder.get_game_name(game_path)
        return {"id": title_id, "name": game_name, "path": game_path, "type": console_type}

    @staticmethod
    def get_title_id(game_path):
        """
        Reads the first 6 bytes at the appropriate offset to get the title ID.
        """
        with open(game_path, "rb") as f:
            offset = 0x0 if game_path.endswith(".iso") else 0x200
            f.seek(offset)
            return f.read(6).decode("ascii", errors="ignore")

    @staticmethod
    def get_game_name(game_path):
        """
        Reads 64 bytes at the appropriate offset to get the game name.
        """
        with open(game_path, "rb") as f:
            offset = 0x20 if game_path.endswith(".iso") else 0x220
            f.seek(offset)
            return f.read(64).decode("ascii", errors="ignore").strip("\x00").strip()

    @staticmethod
    def get_console_type(base_folder, root, file_name, default_type):
        """
        Determines the console type using the default folder type or folder name heuristics.
        """
        if file_name.endswith(".wbfs"):
            return "Wii"
        if default_type in ["Wii", "Gamecube"]:
            return default_type
        norm_root = os.path.normpath(root).lower()
        if "wbfs" in norm_root:
            return "Wii"
        if "games" in norm_root:
            return "Gamecube"
        return "Unknown"
