import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
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
        html_path = os.path.join(current_dir, 'index.html')
        self.webview.setUrl(QUrl.fromLocalFile(html_path))

        # You can also connect to the loadFinished signal to know when the page is ready
        self.webview.loadFinished.connect(self.on_web_load_finished)
        # Add the QWebEngineView to the layout
        layout.addWidget(self.webview)
        self.setLayout(layout)
        
    def on_web_load_finished(self, ok):
        if ok:
            print("Web page loaded successfully!")
        else:
            print("Web page failed to load.")

if __name__ == "__main__":
    # Set the remote debugging port. You can use any free port.
    # You can then access the inspector by opening http://localhost:8080 in a browser.
    # Only needed for debugging
    # os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())