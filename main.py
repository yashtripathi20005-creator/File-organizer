"""
File Organizer - Main Application
A simple GUI tool to organize and rename files in a folder
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from gui import FileOrganizerGUI

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("File Organizer")
    app.setOrganizationName("FileTools")
    
    window = FileOrganizerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
