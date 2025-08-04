import os
import sys

def resource_path(relative_path):
    try:
        Base_path = sys._MEIPASS
    except AttributeError:
        Base_path = os.path.abspath(".")
    return os.path.join(Base_path, relative_path)