from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
                           QCheckBox, QLabel, QFileDialog, QGroupBox)
from PyQt6.QtCore import pyqtSignal

class SettingsTab(QWidget):
    """Onglet pour configurer les paramètres de l'application"""
    
    settings_changed_signal = pyqtSignal(dict)
    links_import_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        
        # Groupe pour les paramètres du navigateur
        browser_group = QGroupBox("Paramètres du navigateur")
        browser_layout = QFormLayout()
        
        self.chrome_path_edit = QLineEdit()
        self.chrome_path_button = QPushButton("Parcourir...")
        
        chrome_path_layout = QHBoxLayout()
        chrome_path_layout.addWidget(self.chrome_path_edit)
        chrome_path_layout.addWidget(self.chrome_path_button)
        
        self.wait_delay_spin = QDoubleSpinBox()
        self.wait_delay_spin.setRange(0.1, 10.0)
        self.wait_delay_spin.setSingleStep(0.1)
        self.wait_delay_spin.setValue(0.3)
        
        self.auto_download_driver_checkbox = QCheckBox("Télécharger automatiquement le driver Chrome")
        self.auto_download_driver_checkbox.setChecked(True)
        
        browser_layout.addRow("Chemin Chrome:", chrome_path_layout)
        browser_layout.addRow("Délai d'attente (s):", self.wait_delay_spin)
        browser_layout.addRow(self.auto_download_driver_checkbox)
        
        browser_group.setLayout(browser_layout)
        
        # Groupe pour les paramètres de participation
        participation_group = QGroupBox("Paramètres de participation")
        participation_layout = QFormLayout()
        
        self.auto_close_tabs_checkbox = QCheckBox("Fermer automatiquement les onglets")
        self.auto_close_tabs_checkbox.setChecked(True)
        
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(1, 5)
        self.retry_attempts_spin.setValue(3)
        
        participation_layout.addRow(self.auto_close_tabs_checkbox)
        participation_layout.addRow("Tentatives en cas d'échec:", self.retry_attempts_spin)
        
        participation_group.setLayout(participation_layout)
        
        # Groupe pour la gestion des liens
        links_group = QGroupBox("Gestion des liens")
        links_layout = QVBoxLayout()
        
        links_buttons_layout = QHBoxLayout()
        
        self.import_links_button = QPushButton("Importer des liens")
        self.export_links_button = QPushButton("Exporter les liens")
        
        links_buttons_layout.addWidget(self.import_links_button)
        links_buttons_layout.addWidget(self.export_links_button)
        links_buttons_layout.addStretch()
        
        links_layout.addLayout(links_buttons_layout)
        
        links_group.setLayout(links_layout)
        
        # Boutons de sauvegarde et réinitialisation
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Sauvegarder")
        self.reset_button = QPushButton("Réinitialiser")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.reset_button)
        
        # Connecter les signaux
        self.chrome_path_button.clicked.connect(self._on_chrome_path_clicked)
        self.import_links_button.clicked.connect(self._on_import_links_clicked)
        self.export_links_button.clicked.connect(self._on_export_links_clicked)
        self.save_button.clicked.connect(self._on_save_clicked)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        
        # Ajouter les widgets au layout principal
        main_layout.addWidget(browser_group)
        main_layout.addWidget(participation_group)
        main_layout.addWidget(links_group)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
    
    def _on_chrome_path_clicked(self):
        """Ouvre une boîte de dialogue pour sélectionner le chemin de Chrome"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner Chrome.exe", "", "Executable Files (*.exe)"
        )
        if file_path:
            self.chrome_path_edit.setText(file_path)
    
    def _on_import_links_clicked(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier JSON contenant des liens"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer des liens", "", "JSON Files (*.json)"
        )
        if file_path:
            self.links_import_signal.emit(file_path)
    
    def _on_export_links_clicked(self):
        """Ouvre une boîte de dialogue pour sélectionner où enregistrer les liens"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les liens", "", "JSON Files (*.json)"
        )
        if file_path:
            return file_path
    
    def _on_save_clicked(self):
        """Enregistre les paramètres"""
        settings = {
            "chrome_path": self.chrome_path_edit.text(),
            "wait_delay": self.wait_delay_spin.value(),
            "auto_download_driver": self.auto_download_driver_checkbox.isChecked(),
            "auto_close_tabs": self.auto_close_tabs_checkbox.isChecked(),
            "retry_attempts": self.retry_attempts_spin.value(),
        }
        self.settings_changed_signal.emit(settings)
    
    def _on_reset_clicked(self):
        """Réinitialise les paramètres à leur valeur par défaut"""
        self.chrome_path_edit.setText("")
        self.wait_delay_spin.setValue(0.3)
        self.auto_download_driver_checkbox.setChecked(True)
        self.auto_close_tabs_checkbox.setChecked(True)
        self.retry_attempts_spin.setValue(3)
    
    def load_settings(self, settings: dict):
        """Charge les paramètres dans l'interface"""
        if "chrome_path" in settings:
            self.chrome_path_edit.setText(settings["chrome_path"])
        if "wait_delay" in settings:
            self.wait_delay_spin.setValue(settings["wait_delay"])
        if "auto_download_driver" in settings:
            self.auto_download_driver_checkbox.setChecked(settings["auto_download_driver"])
        if "auto_close_tabs" in settings:
            self.auto_close_tabs_checkbox.setChecked(settings["auto_close_tabs"])
        if "retry_attempts" in settings:
            self.retry_attempts_spin.setValue(settings["retry_attempts"])