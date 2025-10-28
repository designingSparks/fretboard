import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Fretboard Viewer")
        self.setGeometry(100, 100, 1000, 700) # x, y, width, height - Adjusted for web content

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a QWebEngineView
        self.webview = QWebEngineView()
        
        # Enable developer tools (web inspector) and allow local files to access remote URLs
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Set the zoom factor for the web content (0.75 for 75%)
        self.webview.setZoomFactor(0.75)
        
        # Construct the path to index.html relative to the script's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'fretboard.html')
        self.webview.setUrl(QUrl.fromLocalFile(html_path))

        # You can also connect to the loadFinished signal to know when the page is ready
        self.webview.loadFinished.connect(self.on_web_load_finished)
        # Add the QWebEngineView to the layout
        layout.addWidget(self.webview)

        # Add a Python button to trigger the bend animation
        self.python_bend_button = QPushButton("Python Bend (G string, 9th fret, whole tone)")
        self.python_bend_button.clicked.connect(self._on_python_bend_button_click)
        layout.addWidget(self.python_bend_button)
        
        # Add a second Python button to trigger a half-tone bend animation
        self.python_half_bend_button = QPushButton("Python Bend (B string, 10th fret, half tone)")
        self.python_half_bend_button.clicked.connect(self._on_python_half_bend_button_click)
        layout.addWidget(self.python_half_bend_button)

        self.setLayout(layout)
        
    def on_web_load_finished(self, ok):
        if ok:
            print("Web page loaded successfully!")
            # You could trigger a bend here for initial testing if needed
            # self.animateBend(2, 9, 2) # Example: G string, 9th fret, whole tone
        else:
            print("Web page failed to load.")

    def _on_python_bend_button_click(self):
        """
        Handler for the Python button click. Triggers an example bend animation.
        """
        # Example: G string (index 2), 9th fret, whole tone (2 halftones)
        self.animateBend(2, 9, 2)
        print("Python requested bend animation.")

    def _on_python_half_bend_button_click(self):
        """
        Handler for the second Python button click. Triggers a half-tone bend animation.
        """
        # Example: B string (index 1), 10th fret, half tone (1 halftone)
        self.animateBend(1, 10, 1)
        print("Python requested half-tone bend animation.")

    def animateBend(self, string_index: int, fret: int, halftones: int):
        """
        Sends a command to the QWebEngineView to trigger a bend animation.
        This function is called from Python and executes JavaScript in the web view.

        :param string_index: The 0-based index of the string (e.g., 0 for high e, 5 for low E).
        :param fret: The 1-based fret number.
        :param halftones: 1 for a half-tone bend, 2 for a whole-tone bend.
        """
        if not (0 <= string_index <= 5):
            print(f"Error: Invalid string index {string_index}. Must be between 0 and 5.")
            return
        if not (1 <= fret): # Fret can be any positive integer, assuming NUM_FRETS is handled by JS
            print(f"Error: Invalid fret number {fret}. Must be 1 or greater.")
            return
        if halftones not in [1, 2]:
            print(f"Error: Invalid halftones value {halftones}. Must be 1 or 2.")
            return

        # Construct the JavaScript call to the wrapper function in main.js
        js_code = f"handlePythonBendRequest({string_index}, {fret}, {halftones});"
        self.webview.page().runJavaScript(js_code)
        print(f"Executed JavaScript: {js_code}")

if __name__ == "__main__":
    # Set the remote debugging port. You can use any free port.
    # You can then access the inspector by opening http://localhost:8080 in a browser.
    # Only needed for debugging
    # os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())