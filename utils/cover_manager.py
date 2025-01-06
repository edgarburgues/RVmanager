import os
import requests
from PIL import Image, ImageTk

class CoverManager:
    """
    Handles downloading and loading cover images for games.
    """
    def __init__(self, covers_folder="assets/covers"):
        """
        Ensures the covers folder exists.
        """
        self.covers_folder = os.path.normpath(covers_folder)
        os.makedirs(self.covers_folder, exist_ok=True)

    def download_cover(self, title_id, regions=None):
        """
        Fetches the cover image from GameTDB or returns None if not found.
        """
        if not regions:
            regions = ["US", "EN", "EU", "JP"]
        cover_path = os.path.join(self.covers_folder, f"{title_id}.png")
        if os.path.exists(cover_path):
            return cover_path
        for region in regions:
            url = f"https://art.gametdb.com/wii/cover/{region}/{title_id}.png"
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(cover_path, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    return cover_path
            except:
                pass
        return None

    def load_cover_image(self, cover_path):
        """
        Loads and returns a resized cover image.
        """
        if os.path.exists(cover_path):
            img = Image.open(cover_path).resize((160, 224), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None
