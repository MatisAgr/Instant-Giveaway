from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QLineEdit, QMessageBox, QLabel, 
                           QMenu, QInputDialog, QListWidgetItem, QProgressDialog, 
                           QTextEdit, QDialog, QDialogButtonBox)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QAction, QCursor, QColor, QBrush

import requests
from enum import Enum
import re
import traceback
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LinkVerifier')

class LinkStatus(Enum):
    UNKNOWN = 0
    ACTIVE = 1     # Giveaway actif ou terminé avec gagnant
    DEAD = 2       # Lien mort (404)
    ERROR = 3      # Erreur lors de la vérification

class LogDialog(QDialog):
    """Dialogue pour afficher les logs détaillés"""
    def __init__(self, title, logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 400)
        
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(logs)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class LinkVerifier(QThread):
    """Thread pour vérifier l'état des liens sans bloquer l'interface"""
    link_status_signal = pyqtSignal(str, LinkStatus)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    
    def __init__(self, links):
        super().__init__()
        self.links = links
        self.status_count = {
            LinkStatus.ACTIVE: 0,
            LinkStatus.DEAD: 0,
            LinkStatus.ERROR: 0
        }
        self.logs = []
        
    def log(self, message):
        """Ajoute un message au log et émet un signal"""
        logger.debug(message)
        self.logs.append(message)
        self.log_signal.emit(message)
        
    def run(self):
        total = len(self.links)
        self.log(f"Début de la vérification de {total} liens")
        
        for i, link in enumerate(self.links):
            try:
                self.log(f"Vérification de: {link}")
                
                # Configurer la requête avec un user-agent pour éviter les blocages
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Utiliser GET pour récupérer le contenu
                self.log("Envoi de la requête GET...")
                response = requests.get(link, headers=headers, timeout=15, allow_redirects=True)
                self.log(f"Code de statut: {response.status_code}")
                
                if response.status_code == 200:
                    # Le lien est actif
                    status = LinkStatus.ACTIVE
                    self.status_count[LinkStatus.ACTIVE] += 1
                    
                    # Vérifier si le giveaway est terminé avec un gagnant
                    if 'class="nickname"' in response.text and 'class="finished"' in response.text:
                        self.log("Détecté comme giveaway terminé avec un gagnant")
                    else:
                        self.log("Détecté comme giveaway actif")
                        
                elif response.status_code == 404:
                    # Le lien est mort
                    status = LinkStatus.DEAD
                    self.status_count[LinkStatus.DEAD] += 1
                    self.log("Lien détecté comme mort (404)")
                else:
                    # Autre code d'état HTTP, considéré comme une erreur
                    status = LinkStatus.ERROR
                    self.status_count[LinkStatus.ERROR] += 1
                    self.log(f"Erreur HTTP: {response.status_code}")
                    self.log(f"Réponse: {response.text[:200]}...")  # Afficher le début du texte de réponse
            except Exception as e:
                # Erreur lors de la requête
                status = LinkStatus.ERROR
                self.status_count[LinkStatus.ERROR] += 1
                self.log(f"Exception: {type(e).__name__}: {str(e)}")
                self.log(traceback.format_exc())
            
            self.link_status_signal.emit(link, status)
            self.progress_signal.emit(i + 1)
        
        self.log(f"Vérification terminée. Résultats: Actifs: {self.status_count[LinkStatus.ACTIVE]}, "
                f"Morts: {self.status_count[LinkStatus.DEAD]}, "
                f"Erreurs: {self.status_count[LinkStatus.ERROR]}")
        
        self.finished_signal.emit(self.status_count)

    def _is_finished_with_winner(self, html_content):
        """Vérifie si un giveaway est terminé avec un gagnant"""
        # Recherche des indices dans le HTML qui indiqueraient un giveaway terminé
        return 'class="nickname"' in html_content and 'class="finished"' in html_content

class LinksTab(QWidget):
    """Onglet pour gérer les liens de giveaway"""
    
    links_changed_signal = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.link_status = {}  # Pour stocker l'état de chaque lien
        self.init_ui()
        
    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Titre et instructions
        title_label = QLabel("Gestion des liens de giveaway")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        instructions_label = QLabel("Ajoutez, modifiez ou supprimez des liens. Clic droit sur un lien pour plus d'options.")
        
        # Champ de recherche et bouton de vérification
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un lien...")
        self.search_input.textChanged.connect(self._on_search_changed)
        
        self.verify_button = QPushButton("Vérifier l'état des liens")
        self.verify_button.clicked.connect(self._on_verify_links)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.verify_button)
        
        # Liste des liens
        self.links_list = QListWidget()
        self.links_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.links_list.customContextMenuRequested.connect(self._show_context_menu)
        
        # Boutons d'ajout et de gestion
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter un lien")
        self.add_button.clicked.connect(self._on_add_clicked)
        
        self.remove_button = QPushButton("Supprimer le lien sélectionné")
        self.remove_button.clicked.connect(self._on_remove_clicked)
        self.remove_button.setEnabled(False)
        
        self.save_button = QPushButton("Enregistrer les modifications")
        self.save_button.clicked.connect(self._on_save_clicked)
        
        # Connecter la sélection de la liste pour activer/désactiver le bouton de suppression
        self.links_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        self.total_links_label = QLabel("Total: 0 liens")
        self.status_label = QLabel("")
        stats_layout.addWidget(self.total_links_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.status_label)
        
        # Légende des statuts
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Légende: "))
        
        active_label = QLabel("Actif/Terminé avec gagnant")
        active_label.setStyleSheet("color: green;")
        legend_layout.addWidget(active_label)
        
        dead_label = QLabel("Lien mort (404)")
        dead_label.setStyleSheet("color: red;")
        legend_layout.addWidget(dead_label)
        
        error_label = QLabel("Erreur de vérification")
        error_label.setStyleSheet("color: orange;")
        legend_layout.addWidget(error_label)
        
        legend_layout.addStretch()
        
        legend_layout.addStretch()
        
        # Ajouter les widgets au layout principal
        layout.addWidget(title_label)
        layout.addWidget(instructions_label)
        layout.addLayout(search_layout)
        layout.addWidget(self.links_list)
        layout.addLayout(buttons_layout)
        layout.addLayout(stats_layout)
        layout.addLayout(legend_layout)
    
    def load_links(self, links):
        """Charge les liens dans la liste"""
        self.links = links.copy()
        self._update_list()
        
    def _update_list(self):
        """Met à jour la liste des liens affichés"""
        self.links_list.clear()
        
        for link in self.links:
            item = QListWidgetItem(link)
            
            # Appliquer la coloration selon le statut s'il existe
            if link in self.link_status:
                status = self.link_status[link]
                if status == LinkStatus.ACTIVE:
                    item.setForeground(QBrush(QColor("green")))
                elif status == LinkStatus.DEAD:
                    item.setForeground(QBrush(QColor("red")))
                elif status == LinkStatus.ERROR:
                    item.setForeground(QBrush(QColor("orange")))
            
            self.links_list.addItem(item)
            
        self.total_links_label.setText(f"Total: {len(self.links)} liens")
    
    def _on_verify_links(self):
        """Vérifie l'état de tous les liens"""
        if not self.links:
            QMessageBox.information(
                self,
                "Aucun lien",
                "Il n'y a aucun lien à vérifier."
            )
            return
            
        # Désactiver le bouton pendant la vérification
        self.verify_button.setEnabled(False)
        
        # Créer et configurer la boîte de dialogue de progression améliorée
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Vérification en cours")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.resize(500, 300)
        
        # Layout principal
        layout = QVBoxLayout(progress_dialog)
        
        # Label d'information
        info_label = QLabel("Vérification des liens en cours...")
        layout.addWidget(info_label)
        
        # Barre de progression
        progress_bar = QProgressDialog("Vérification des liens...", "Annuler", 0, len(self.links), progress_dialog)
        progress_bar.setWindowModality(Qt.WindowModality.NonModal)
        progress_bar.setAutoClose(False)
        progress_bar.setWindowFlags(Qt.WindowType.Widget)  # Pour éviter qu'elle ne s'affiche comme une fenêtre séparée
        layout.addWidget(progress_bar)
        
        # Compteur de progression
        counter_label = QLabel(f"0/{len(self.links)}")
        counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(counter_label)
        
        # Zone de logs
        log_area = QTextEdit()
        log_area.setReadOnly(True)
        log_area.setMaximumHeight(150)
        layout.addWidget(log_area)
        
        # Créer le journal de logs
        self.verification_logs = []
        
        # Créer et démarrer le thread de vérification
        self.verifier = LinkVerifier(self.links)
        
        # Connecter les signaux
        self.verifier.link_status_signal.connect(self._update_link_status)
        self.verifier.progress_signal.connect(progress_bar.setValue)
        self.verifier.progress_signal.connect(
            lambda value: counter_label.setText(f"{value}/{len(self.links)}")
        )
        self.verifier.finished_signal.connect(self._verification_completed)
        self.verifier.finished_signal.connect(progress_dialog.close)
        
        # Gérer les logs
        def update_logs(msg):
            self.verification_logs.append(msg)
            log_area.append(msg)
            # Défiler automatiquement vers le bas
            log_area.verticalScrollBar().setValue(log_area.verticalScrollBar().maximum())
        
        self.verifier.log_signal.connect(update_logs)
        
        # Connecter l'annulation
        progress_bar.canceled.connect(self.verifier.terminate)
        progress_bar.canceled.connect(self._on_verification_canceled)
        progress_bar.canceled.connect(progress_dialog.close)
        
        # Démarrer la vérification
        self.verifier.start()
        
        # Afficher la boîte de dialogue
        progress_dialog.exec()
    
    def _on_verification_canceled(self):
        """Réactive le bouton de vérification lorsque l'opération est annulée"""
        self.verify_button.setEnabled(True)
    
    @pyqtSlot(str, LinkStatus)
    def _update_link_status(self, link, status):
        """Met à jour le statut d'un lien"""
        self.link_status[link] = status
        
        # Mettre à jour l'affichage si le lien est actuellement visible
        for i in range(self.links_list.count()):
            item = self.links_list.item(i)
            if item.text() == link:
                if status == LinkStatus.ACTIVE:
                    item.setForeground(QBrush(QColor("green")))
                elif status == LinkStatus.DEAD:
                    item.setForeground(QBrush(QColor("red")))
                elif status == LinkStatus.ERROR:
                    item.setForeground(QBrush(QColor("orange")))
                break
    
    @pyqtSlot(dict)
    def _verification_completed(self, status_count):
        """Appelé lorsque la vérification est terminée"""
        self.verify_button.setEnabled(True)
        
        # Mettre à jour les statistiques
        active = status_count[LinkStatus.ACTIVE]
        dead = status_count[LinkStatus.DEAD]
        error = status_count[LinkStatus.ERROR]
        
        self.status_label.setText(
            f"Actifs: {active} | Morts: {dead} | Erreurs: {error}"
        )
        
        # Afficher un message récapitulatif
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Vérification terminée")
        msg_box.setText(
            f"Résultats de la vérification:\n"
            f"- Liens actifs ou terminés avec gagnant: {active}\n"
            f"- Liens morts (404): {dead}\n"
            f"- Erreurs de vérification: {error}"
        )
        
        # Ajouter un bouton pour voir les logs détaillés
        show_logs_button = msg_box.addButton("Voir les logs", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        
        # Afficher la boîte de dialogue
        msg_box.exec()
        
        # Vérifier si le bouton "Voir les logs" a été cliqué
        if msg_box.clickedButton() == show_logs_button:
            logs_text = "\n".join(self.verification_logs)
            log_dialog = LogDialog("Logs de vérification", logs_text, self)
            log_dialog.exec()
    
    def _on_add_clicked(self):
        """Ajoute un nouveau lien"""
        link, ok = QInputDialog.getText(
            self, 
            "Ajouter un lien", 
            "Entrez l'URL du giveaway (format: https://www.instant-gaming.com/XX/giveaway/INFLUENCER):"
        )
        
        if ok and link:
            # Validation basique du lien
            if not link.startswith('https://www.instant-gaming.com/') or '/giveaway/' not in link:
                QMessageBox.warning(
                    self, 
                    "Format invalide", 
                    "Le lien doit être au format:\nhttps://www.instant-gaming.com/XX/giveaway/INFLUENCER"
                )
                return
                
            if link not in self.links:
                self.links.append(link)
                self._update_list()
                # Sélectionner le nouveau lien
                self.links_list.setCurrentRow(self.links_list.count() - 1)
            else:
                QMessageBox.information(
                    self, 
                    "Lien existant", 
                    "Ce lien existe déjà dans la liste."
                )
    
    def _on_remove_clicked(self):
        """Supprime le lien sélectionné"""
        current_row = self.links_list.currentRow()
        if current_row >= 0:
            link = self.links[current_row]
            reply = QMessageBox.question(
                self, 
                "Confirmer la suppression", 
                f"Êtes-vous sûr de vouloir supprimer ce lien?\n\n{link}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Supprimer aussi le statut du lien s'il existe
                if link in self.link_status:
                    del self.link_status[link]
                    
                del self.links[current_row]
                self._update_list()
    
    def _on_save_clicked(self):
        """Enregistre les modifications"""
        self.links_changed_signal.emit(self.links)
        QMessageBox.information(
            self, 
            "Sauvegarde réussie", 
            f"{len(self.links)} liens ont été sauvegardés avec succès."
        )
    
    def _on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        self.remove_button.setEnabled(self.links_list.currentRow() >= 0)
    
    def _on_search_changed(self, text):
        """Filtre la liste en fonction du texte de recherche"""
        if not text:
            # Si le champ est vide, afficher tous les liens
            self._update_list()
            return
            
        # Filtrer les liens
        text = text.lower()
        self.links_list.clear()
        
        filtered_count = 0
        for link in self.links:
            if text in link.lower():
                item = QListWidgetItem(link)
                
                # Appliquer la coloration selon le statut s'il existe
                if link in self.link_status:
                    status = self.link_status[link]
                    if status == LinkStatus.ACTIVE:
                        item.setForeground(QBrush(QColor("green")))
                    elif status == LinkStatus.DEAD:
                        item.setForeground(QBrush(QColor("red")))
                    elif status == LinkStatus.ERROR:
                        item.setForeground(QBrush(QColor("orange")))
                
                self.links_list.addItem(item)
                filtered_count += 1
        
        self.total_links_label.setText(f"Affichés: {filtered_count} sur {len(self.links)} liens")
    
    def _show_context_menu(self, position):
        """Affiche le menu contextuel lors d'un clic droit sur un lien"""
        item = self.links_list.itemAt(position)
        
        if item:
            current_row = self.links_list.currentRow()
            link = self.links[current_row]
            
            menu = QMenu()
            edit_action = QAction("Modifier", self)
            copy_action = QAction("Copier", self)
            verify_action = QAction("Vérifier ce lien", self)
            remove_action = QAction("Supprimer", self)
            
            menu.addAction(edit_action)
            menu.addAction(copy_action)
            menu.addAction(verify_action)
            menu.addSeparator()
            menu.addAction(remove_action)
            
            # Connecter les actions
            edit_action.triggered.connect(lambda: self._edit_link(current_row))
            copy_action.triggered.connect(lambda: self._copy_to_clipboard(link))
            verify_action.triggered.connect(lambda: self._verify_single_link(link))
            remove_action.triggered.connect(self._on_remove_clicked)
            
            # Afficher le menu à la position du curseur
            menu.exec(QCursor.pos())
    
    
    
    def _verify_single_link(self, link):
        """Vérifie l'état d'un seul lien"""
        # Liste pour stocker les logs
        logs = []
        
        try:
            # Afficher un dialogue de progression non annulable
            progress = QProgressDialog("Vérification du lien...", None, 0, 0, self)
            progress.setWindowTitle("Vérification en cours")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setCancelButton(None)  # Pas de bouton d'annulation
            progress.show()
            
            logs.append(f"Vérification du lien: {link}")
            
            # Configurer la requête avec un user-agent pour éviter les blocages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logs.append("Envoi de la requête GET...")
            
            # Vérifier le lien avec GET pour obtenir le contenu
            response = requests.get(link, headers=headers, timeout=15, allow_redirects=True)
            
            logs.append(f"Code de statut: {response.status_code}")
            
            # Déterminer le statut
            if response.status_code == 200:
                # Vérifier si c'est un giveaway actif ou terminé avec gagnant
                status = LinkStatus.ACTIVE
                
                # Vérifier si le giveaway est terminé avec un gagnant
                if 'class="nickname"' in response.text and 'class="finished"' in response.text:
                    status_text = "terminé avec gagnant"
                    logs.append("Détecté comme giveaway terminé avec un gagnant")
                else:
                    status_text = "actif"
                    logs.append("Détecté comme giveaway actif")
                    
                color = "green"
            elif response.status_code == 404:
                status = LinkStatus.DEAD
                status_text = "mort (404)"
                color = "red"
                logs.append("Lien détecté comme mort (404)")
            else:
                status = LinkStatus.ERROR
                status_text = f"erreur ({response.status_code})"
                color = "orange"
                logs.append(f"Erreur HTTP: {response.status_code}")
                logs.append(f"Début de la réponse: {response.text[:200]}...")
                
            # Mettre à jour le statut du lien
            self.link_status[link] = status
            
            # Mettre à jour l'affichage
            for i in range(self.links_list.count()):
                item = self.links_list.item(i)
                if item.text() == link:
                    item.setForeground(QBrush(QColor(color)))
                    break
            
            # Fermer le dialogue de progression
            progress.close()
            
            # Créer la boîte de dialogue de résultat
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Vérification terminée")
            msg_box.setText(f"Le lien est <span style='color:{color};'>{status_text}</span>.")
            
            # Ajouter un bouton pour voir les logs détaillés
            show_logs_button = msg_box.addButton("Voir les logs", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(QMessageBox.StandardButton.Ok)
            
            # Afficher la boîte de dialogue
            msg_box.exec()
            
            # Vérifier si le bouton "Voir les logs" a été cliqué
            if msg_box.clickedButton() == show_logs_button:
                log_dialog = LogDialog("Logs de vérification", "\n".join(logs), self)
                log_dialog.exec()
            
        except Exception as e:
            # En cas d'erreur
            self.link_status[link] = LinkStatus.ERROR
            
            # Détails de l'exception
            logs.append(f"Exception: {type(e).__name__}: {str(e)}")
            logs.append(traceback.format_exc())
            
            # Mettre à jour l'affichage
            for i in range(self.links_list.count()):
                item = self.links_list.item(i)
                if item.text() == link:
                    item.setForeground(QBrush(QColor("orange")))
                    break
            
            # Fermer le dialogue de progression
            progress.close()
            
            # Créer la boîte de dialogue d'erreur
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Erreur de vérification")
            msg_box.setText(f"Erreur lors de la vérification du lien:\n{str(e)}")
            
            # Ajouter un bouton pour voir les logs détaillés
            show_logs_button = msg_box.addButton("Voir les logs détaillés", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(QMessageBox.StandardButton.Ok)
            
            # Afficher la boîte de dialogue
            msg_box.exec()
            
            # Vérifier si le bouton "Voir les logs" a été cliqué
            if msg_box.clickedButton() == show_logs_button:
                log_dialog = LogDialog("Logs d'erreur", "\n".join(logs), self)
                log_dialog.exec()
    
    
    def _edit_link(self, row):
        """Modifie un lien existant"""
        if row >= 0 and row < len(self.links):
            current_link = self.links[row]
            new_link, ok = QInputDialog.getText(
                self, 
                "Modifier le lien", 
                "Modifier l'URL du giveaway:",
                QLineEdit.EchoMode.Normal,
                current_link
            )
            
            if ok and new_link and new_link != current_link:
                # Validation basique du lien
                if not new_link.startswith('https://www.instant-gaming.com/') or '/giveaway/' not in new_link:
                    QMessageBox.warning(
                        self, 
                        "Format invalide", 
                        "Le lien doit être au format:\nhttps://www.instant-gaming.com/XX/giveaway/INFLUENCER"
                    )
                    return
                    
                if new_link in self.links:
                    QMessageBox.information(
                        self, 
                        "Lien existant", 
                        "Ce lien existe déjà dans la liste."
                    )
                    return
                
                # Si l'ancien lien avait un statut, le transférer au nouveau
                if current_link in self.link_status:
                    self.link_status[new_link] = self.link_status[current_link]
                    del self.link_status[current_link]
                
                self.links[row] = new_link
                self._update_list()
                # Resélectionner le lien
                self.links_list.setCurrentRow(row)
    
    def _copy_to_clipboard(self, text):
        """Copie le texte dans le presse-papier"""
        clipboard = self.window().clipboard()
        clipboard.setText(text)
        
        # Notification temporaire
        QMessageBox.information(
            self,
            "Copié",
            "Le lien a été copié dans le presse-papier."
        )