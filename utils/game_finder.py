import os

def get_disc_number_iso_offset_6(iso_path):
    """
    Reads offset 0x006 in a GameCube ISO to determine disc number.
    """
    if not os.path.isfile(iso_path):
        return 1
    with open(iso_path, "rb") as f:
        f.seek(6)
        disc_byte = f.read(1)
        if not disc_byte:
            return 1
        val = disc_byte[0]
        if val == 0x00:
            return 1
        elif val == 0x01:
            return 2
        return 1

class GameFinder:
    """
    Finds and extracts metadata from .iso or .wbfs files.
    """
    @staticmethod
    def find_games(folders, extensions=(".iso", ".wbfs")):
        """
        Searches for valid game files under the specified folders.
        """
        games = []
        for folder in folders:
            folder_path = os.path.normpath(folder["path"])
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(extensions):
                        game_path = os.path.normpath(os.path.join(root, file))
                        console_type = GameFinder.get_console_type(folder_path, root, file, folder["type"])
                        games.append(GameFinder.extract_game_info(game_path, console_type))
        return games

    @staticmethod
    def extract_game_info(game_path, console_type):
        """
        Extracts title ID, name, type, and disc number from a game file.
        """
        title_id = GameFinder.get_title_id(game_path)
        game_name = GameFinder.get_game_name(game_path)
        disc_number = 1
        if console_type == "Gamecube":
            disc_number = get_disc_number_iso_offset_6(game_path)
        return {
            "id": title_id,
            "name": game_name,
            "path": game_path,
            "type": console_type,
            "disc_number": disc_number
        }

    @staticmethod
    def get_title_id(game_path):
        """
        Retrieves the first 6 bytes from offset 0x0 (ISO) or 0x200 (WBFS).
        """
        with open(game_path, "rb") as f:
            offset = 0x0 if game_path.lower().endswith(".iso") else 0x200
            f.seek(offset)
            return f.read(6).decode("ascii", errors="ignore")

    @staticmethod
    def get_game_name(game_path):
        """
        Retrieves up to 64 bytes for the internal game name.
        """
        with open(game_path, "rb") as f:
            offset = 0x20 if game_path.lower().endswith(".iso") else 0x220
            f.seek(offset)
            return f.read(64).decode("ascii", errors="ignore").strip("\x00").strip()

    @staticmethod
    def get_console_type(base_folder, root, file_name, default_type):
        """
        Determines the console type (Gamecube/Wii/Unknown).
        """
        if file_name.lower().endswith(".wbfs"):
            return "Wii"
        if default_type in ["Wii", "Gamecube"]:
            return default_type
        norm_root = os.path.normpath(root).lower()
        if "wbfs" in norm_root:
            return "Wii"
        if "games" in norm_root:
            return "Gamecube"
        return "Unknown"

    @staticmethod
    def get_region(game_path):
        """
        Reads offset 0x03 to determine the region code.
        """
        with open(game_path, "rb") as f:
            f.seek(0x03)
            region_code = f.read(1)
            regions = {
                b'\x00': "Japan",
                b'\x01': "USA",
                b'\x02': "Europe"
            }
            return regions.get(region_code, "Unknown")

    @staticmethod
    def get_version(game_path):
        """
        Reads offset 0x07 to determine the disc version.
        """
        with open(game_path, "rb") as f:
            f.seek(0x07)
            return int.from_bytes(f.read(1), "big")
