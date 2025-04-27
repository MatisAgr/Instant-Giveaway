# -*- coding: utf-8 -*-
"""
Module principal de l'application Instant Giveaway.
Ce module initialise l'application, configure l'icône et lance le contrôleur principal.
Il est responsable de l'affichage de la fenêtre principale et de la gestion de l'application.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.controllers.app_controller import AppController

def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Instant Giveaway")
    app.setOrganizationName("Instant Giveaway")

    # Définir l'icône de l'application
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "img", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialisation du contrôleur principal
    controller = AppController()
    controller.show_main_window()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
