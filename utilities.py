import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for Nuitka/PyInstaller.
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if sys.platform == 'darwin':
                # macOS .app bundle structure
                base_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
            else:
                # Windows/Linux: resources are typically in the same directory as executable
                base_path = os.path.dirname(sys.executable)
        else:
            # Running as a normal .py script
            base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)