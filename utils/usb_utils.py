import os
import shutil

class USBUtils:
    """
    Provides USB drive detection and operations for copying or deleting games.
    """
    @staticmethod
    def get_available_drives():
        """
        Returns a list of available drives in the system.
        """
        if os.name == "nt":
            return [os.path.normpath(f"{chr(d)}:/") for d in range(65, 91) if os.path.exists(f"{chr(d)}:/")]
        else:
            return [os.path.normpath(os.path.join("/media", d)) for d in os.listdir("/media") if os.path.isdir(os.path.join("/media", d))]

    @staticmethod
    def copy_game_to_usb(game, usb_path, cover_manager):
        """
        Copies a game to the USB drive in the appropriate folder structure and ensures the cover is also copied.
        """
        try:
            console_type = game["type"]
            if console_type == "Wii":
                destination_folder = os.path.join(usb_path, "wbfs")
            elif console_type == "Gamecube":
                destination_folder = os.path.join(usb_path, "games", game["id"])
            else:
                return f"{game['name']}: Unknown console type"

            # Copy game file
            os.makedirs(destination_folder, exist_ok=True)
            shutil.copy2(game["path"], os.path.join(destination_folder, "game.iso"))

            # Handle cover
            covers_folder = os.path.join(usb_path, "rvloader", "covers")
            os.makedirs(covers_folder, exist_ok=True)
            cover_path = os.path.join(covers_folder, f"{game['id']}.png")

            if not os.path.exists(cover_path):
                downloaded_cover = cover_manager.download_cover(game["id"])
                if downloaded_cover:
                    shutil.copy2(downloaded_cover, cover_path)
                else:
                    return f"{game['name']}: Copied game, but cover not found"

            return f"{game['name']}: Copied successfully"
        except Exception as e:
            return f"{game['name']}: Copy error ({str(e)})"


    @staticmethod
    def delete_game_from_usb(game, usb_path):
        """
        Deletes a game folder from the USB drive.
        """
        try:
            console_type = game["type"]
            if console_type == "Wii":
                folder = os.path.join(usb_path, "wbfs")
            elif console_type == "Gamecube":
                folder = os.path.join(usb_path, "games", game["id"])
            else:
                return f"{game['name']}: Unknown console type"
            if os.path.exists(folder):
                shutil.rmtree(folder)
                return f"{game['name']}: Deleted successfully"
            else:
                return f"{game['name']}: Not found on USB"
        except Exception as e:
            return f"{game['name']}: Delete error ({str(e)})"
