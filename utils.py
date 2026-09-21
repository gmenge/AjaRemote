import os
import sys
from PIL import Image, ImageTk


def resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def aplicar_icone(janela):
    """Aplica o ícone da aplicação em qualquer janela do Tkinter usando suporte duplo."""
    caminho_ico = resource_path("logo.ico")

    if not os.path.exists(caminho_ico):
        return

    # 1. Tenta o método nativo iconbitmap
    try:
        janela.wm_iconbitmap(caminho_ico)
    except Exception:
        pass

    # 2. Garante a aplicação visual usando iconphoto via PIL
    try:
        img = Image.open(caminho_ico)
        photo = ImageTk.PhotoImage(img)

        # O primeiro argumento True aplica o ícone a esta janela e a todas as futuras Toplevels filhas
        janela.iconphoto(True, photo)

        # Mantém uma referência fixa na instância da janela para evitar garbage collection do Python
        janela._global_icon_ref = photo
    except Exception as e:
        print(f"Erro ao carregar iconphoto: {e}")