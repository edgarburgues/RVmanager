import os

class GameFinder:
    @staticmethod
    def find_games(folders, extensions=('.iso', '.wbfs')):
        """
        Busca juegos en formato .iso o .wbfs en las carpetas especificadas.
        Retorna una lista de diccionarios con la info de cada juego.
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
        Extrae el ID y el nombre de un juego a partir del archivo ISO/WBFS.
        """
        title_id = GameFinder.get_title_id(game_path)
        game_name = GameFinder.get_game_name(game_path)
        return {"id": title_id, "name": game_name, "path": game_path, "type": console_type}

    @staticmethod
    def get_title_id(game_path):
        """
        Lee los primeros 6 bytes (offset distinto según .iso o .wbfs) para obtener el ID.
        """
        with open(game_path, 'rb') as f:
            offset = 0x0 if game_path.endswith('.iso') else 0x200
            f.seek(offset)
            return f.read(6).decode('ascii')

    @staticmethod
    def get_game_name(game_path):
        """
        Lee 64 bytes (offset distinto según .iso o .wbfs) para obtener el nombre.
        """
        with open(game_path, 'rb') as f:
            offset = 0x20 if game_path.endswith('.iso') else 0x220
            f.seek(offset)
            return f.read(64).decode('ascii', errors='ignore').strip('\x00').strip()

    @staticmethod
    def get_console_type(folders, root, file):
        """
        Determina si un archivo .wbfs es Wii, 
        o se basa en la carpeta en la que se encuentra para inferir si es Wii o Gamecube.
        """
        if file.endswith('.wbfs'):
            return "Wii"
        
        for folder in folders:
            if os.path.normpath(root).startswith(os.path.normpath(folder["path"])):
                return folder["type"]

        return "Unknown"
