from ui.app import RVLoaderApp
from ttkbootstrap import Style

if __name__ == "__main__":
    style = Style(theme="cosmo")
    root = style.master
    app = RVLoaderApp(root)
    root.mainloop()
