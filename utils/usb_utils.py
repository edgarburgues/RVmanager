import os
import shutil

class USBUtils:
    @staticmethod
    def get_available_drives():
        """
        Returns available drives (Windows or Linux).
        """
        if os.name == 'nt':
            return [os.path.normpath(f"{chr(d)}:/") for d in range(65, 91) if os.path.exists(f"{chr(d)}:/")]
        else:
            return [os.path.normpath(f"/media/{d}") for d in os.listdir("/media/") if os.path.isdir(f"/media/{d}")]

    @staticmethod
    def copy_game_to_usb(game, usb_path):
        """
        Copies a game (ISO/WBFS) to the appropriate structure on the USB drive.
        """
        try:
            console_type = game["type"]
            if console_type == "Wii":
                destination_folder = os.path.join(usb_path, "wbfs")
            elif console_type == "Gamecube":
                destination_folder = os.path.join(usb_path, "games", game["id"])
            else:
                return f"Error: Unknown type for the game {game['name']}"

            os.makedirs(destination_folder, exist_ok=True)
            shutil.copy2(game["path"], os.path.join(destination_folder, "game.iso"))
            return f"{game['name']}: Successfully copied"
        except Exception as e:
            return f"Error copying {game['name']}: {e}"
