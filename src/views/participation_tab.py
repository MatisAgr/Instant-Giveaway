from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QProgressBar, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QLabel, QTextEdit)
from PyQt6.QtCore import pyqtSignal

class ParticipationTab(QWidget):
    """Onglet pour la participation aux giveaways"""
    
    start_participation_signal = pyqtSignal()
    stop_participation_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Boutons de contrôle
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Démarrer la participation")
        self.stop_button = QPushButton("Arrêter")
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        
        # Connecter les signaux
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        
        # Barre de progression
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.status_label = QLabel("Prêt")
        
        progress_layout.addWidget(QLabel("Progression:"))
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        # Tableau des giveaways
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Influenceur", "URL", "Statut", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Zone de logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Ajouter les widgets au layout principal
        layout.addLayout(control_layout)
        layout.addLayout(progress_layout)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_area)
    
    def _on_start_clicked(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_participation_signal.emit()
    
    def _on_stop_clicked(self):
        self.stop_button.setEnabled(False)
        self.stop_participation_signal.emit()
    
    def add_log(self, message: str):
        """Ajoute un message dans la zone de logs"""
        self.log_area.append(message)
    
    def update_progress(self, current: int, total: int):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(int(100 * current / total) if total > 0 else 0)
        self.progress_bar.setFormat(f"{current}/{total} ({int(100 * current / total) if total > 0 else 0}%)")
    
    def update_status(self, status: str):
        """Met à jour le statut affiché"""
        self.status_label.setText(status)
    
    def reset_ui(self):
        """Réinitialise l'interface utilisateur"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Prêt")