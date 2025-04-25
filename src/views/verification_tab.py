from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QLabel, QTextEdit, QProgressBar, QDialog)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor

class VerificationTab(QWidget):
    """Onglet pour vérifier les giveaways gagnés"""
    
    start_verification_signal = pyqtSignal()
    stop_verification_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.username = "En attente..."
        self.init_ui()
        
    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Affichage du pseudo de l'utilisateur avec un style amélioré
        user_layout = QHBoxLayout()
        self.connection_status_icon = QLabel("⚫")  # Point pour indiquer le statut
        self.connection_status_icon.setStyleSheet("color: red;")  # Rouge = non connecté par défaut
        
        self.username_label = QLabel(f"Utilisateur: <b>{self.username}</b>")
        
        user_layout.addWidget(self.connection_status_icon)
        user_layout.addWidget(self.username_label)
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        # Boutons de contrôle
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Vérifier les giveaways")
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
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Influenceur", "URL", "Statut", "Gagnant", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Tableau des giveaways gagnés
        self.wins_label = QLabel("Giveaways gagnés:")
        self.wins_table = QTableWidget(0, 3)
        self.wins_table.setHorizontalHeaderLabels(["Influenceur", "URL", "Date"])
        self.wins_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Zone de logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Ajouter les widgets au layout principal
        layout.addLayout(control_layout)
        layout.addLayout(progress_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.wins_label)
        layout.addWidget(self.wins_table)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_area)
    
    def set_username(self, username):
        """Met à jour le nom d'utilisateur affiché"""
        if username and username.strip():
            self.username = username
            self.username_label.setText(f"Utilisateur: <b>{self.username}</b>")
            # Mettre à jour l'indicateur de statut
            self.connection_status_icon.setText("⚫")
            self.connection_status_icon.setStyleSheet("color: green; font-size: 14px;")
            self.connection_status_icon.setToolTip("Connecté")
            # Ajouter un message dans les logs
            self.add_log(f"Utilisateur connecté: {self.username}")
            # Activer le bouton de vérification
            self.start_button.setEnabled(True)
        else:
            self.username = "Non connecté"
            self.username_label.setText(f"Utilisateur: <b>{self.username}</b>")
            # Mettre à jour l'indicateur de statut
            self.connection_status_icon.setText("⚫")
            self.connection_status_icon.setStyleSheet("color: red; font-size: 14px;")
            self.connection_status_icon.setToolTip("Non connecté")
            self.add_log("Aucun utilisateur connecté")
            # Désactiver le bouton de vérification
            self.start_button.setEnabled(False)
    
    def _on_start_clicked(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_verification_signal.emit()
    
    def _on_stop_clicked(self):
        self.stop_button.setEnabled(False)
        self.stop_verification_signal.emit()
    
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
    
    def add_win(self, influencer: str, url: str, date: str):
        """Ajoute un giveaway gagné au tableau"""
        row_position = self.wins_table.rowCount()
        self.wins_table.insertRow(row_position)
        self.wins_table.setItem(row_position, 0, QTableWidgetItem(influencer))
        self.wins_table.setItem(row_position, 1, QTableWidgetItem(url))
        self.wins_table.setItem(row_position, 2, QTableWidgetItem(date))
        
        # Mettre en surbrillance les lignes des victoires avec une couleur vert foncé
        # qui conserve la lisibilité du texte
        for col in range(3):
            item = self.wins_table.item(row_position, col)
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            # Vert foncé plus adapté à la lecture du texte
            item.setBackground(QColor(120, 180, 120))  # Vert foncé
    
    def reset_ui(self):
        """Réinitialise l'interface utilisateur"""
        # Ne pas réinitialiser l'état du bouton Start si un utilisateur est connecté
        if self.username != "En attente..." and self.username != "Non connecté":
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Prêt")