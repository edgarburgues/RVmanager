import os
import requests
from PIL import Image, ImageTk

class CoverManager:
    """
    Administra las portadas de los juegos (descarga y carga de imágenes).
    """
    def __init__(self, covers_folder="assets/covers"):
        self.covers_folder = os.path.normpath(covers_folder)
        os.makedirs(self.covers_folder, exist_ok=True)

    def download_cover(self, title_id, regions=None):
        """
        Descarga la portada del juego según el ID y región.
        Devuelve la ruta local de la portada o None si no la encontró.
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
        Carga la imagen de portada y la redimensiona a 160x224, 
        retornando un objeto ImageTk.PhotoImage.
        """
        if os.path.exists(cover_path):
            # Para versiones modernas de Pillow, se usa Image.Resampling.LANCZOS
            img = Image.open(cover_path).resize((160, 224), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None
