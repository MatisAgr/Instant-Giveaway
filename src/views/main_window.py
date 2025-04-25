from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from .participation_tab import ParticipationTab
from .verification_tab import VerificationTab
from .settings_tab import SettingsTab
from .links_tab import LinksTab

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instant Giveaway")
        self.resize(800, 600)
        
        # Création du widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Onglets
        self.tabs = QTabWidget()
        self.participation_tab = ParticipationTab()
        self.verification_tab = VerificationTab()
        self.links_tab = LinksTab()
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.participation_tab, "Participation")
        self.tabs.addTab(self.verification_tab, "Vérification")
        self.tabs.addTab(self.links_tab, "Gestion des liens") 
        self.tabs.addTab(self.settings_tab, "Paramètres")
        
        main_layout.addWidget(self.tabs)