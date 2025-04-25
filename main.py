#!/usr/bin/env python3
# filepath: main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.controllers.app_controller import AppController

def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Instant Giveaway")
    app.setOrganizationName("Instant Giveaway")
    
    # Initialisation du contrôleur principal
    controller = AppController()
    controller.show_main_window()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()