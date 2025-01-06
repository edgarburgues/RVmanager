import os
import sys
from ttkbootstrap import Style
from ui.app import RVLoaderApp

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

if __name__ == "__main__":
    style = Style(theme="cosmo")
    root = style.master
    root.title("RVLoader Game Manager")
    app = RVLoaderApp(root, base_dir=get_base_dir())
    root.mainloop()
