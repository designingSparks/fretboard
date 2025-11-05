import os, sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for Nuitka/PyInstaller.
    """
    try:
        # Check if running in a "frozen" bundle (e.g., Nuitka .app)
        if getattr(sys, 'frozen', False):
            # The executable is in Contents/MacOS
            base_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
        else:
            # Running as a normal .py script
            base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)