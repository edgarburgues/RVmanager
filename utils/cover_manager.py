import os
import requests
from PIL import Image, ImageTk

class CoverManager:
    """
    Manages game cover images (downloading and loading).
    """
    def __init__(self, covers_folder="assets/covers"):
        self.covers_folder = os.path.normpath(covers_folder)
        os.makedirs(self.covers_folder, exist_ok=True)

    def download_cover(self, title_id, regions=None):
        """
        Downloads the cover image for a given title ID and region.
        Returns the local path of the cover or None if not found.
        """
        if not regions:
            regions = ["US", "EN", "EU", "JP"]

        cover_path = os.path.normpath(os.path.join(self.covers_folder, f"{title_id}.png"))
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
            except Exception:
                continue
        return None

    def load_cover_image(self, cover_path):
        """
        Loads the cover image and resizes it to 160x224,
        returning an ImageTk.PhotoImage object.
        """
        if os.path.exists(cover_path):
            img = Image.open(cover_path).resize((160, 224), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None
