import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QObject

from src.views.main_window import MainWindow
from src.controllers.browser_controller import BrowserController
from src.controllers.giveaway_controller import GiveawayController
from src.models.settings import Settings
from src.models.giveaway import Giveaway, GiveawayStatus

class AppController(QObject):
    """Contrôleur principal de l'application"""
    
    def __init__(self):
        super().__init__()
        
        # Initialiser les modèles
        self.settings = Settings.load()
        
        # Initialiser les contrôleurs
        self.browser_controller = BrowserController()
        self.browser_controller.set_settings(self.settings)
        self.giveaway_controller = GiveawayController(self.browser_controller)
        
        # Initialiser la vue principale
        self.main_window = MainWindow()
        self.main_window.settings_tab.load_settings(self.settings.__dict__)
        
        # Connecter les signaux
        self._connect_signals()
        
        # Charger les liens
        self._load_links()
        
        # Initialiser l'affichage du nom d'utilisateur
        if not self.settings.auto_detect_username and self.settings.username:
            # Mode manuel avec pseudo défini
            self.main_window.verification_tab.set_username(self.settings.username)
        elif self.settings.auto_detect_username:
            # Mode auto
            self.main_window.verification_tab.set_username("(Auto)")
            if self.settings.username:
                # Si un pseudo par défaut est défini, l'afficher avec la mention Auto
                self.main_window.verification_tab.set_username(f"{self.settings.username} (Auto)")
        else:
            # Aucun pseudo défini
            self.main_window.verification_tab.set_username("Non connecté")
    
    def show_main_window(self):
        """Affiche la fenêtre principale"""
        self.main_window.show()
    
    def _connect_signals(self):
        """Connecter les signaux entre les différents composants"""
        # Signaux de l'onglet de participation
        tab = self.main_window.participation_tab
        tab.start_participation_signal.connect(self._on_start_participation)
        tab.stop_participation_signal.connect(self._on_stop_participation)
        
        # Signaux de l'onglet de vérification
        tab = self.main_window.verification_tab
        tab.start_verification_signal.connect(self._on_start_verification)
        tab.stop_verification_signal.connect(self._on_stop_verification)
        
        # Signaux de l'onglet de paramètres
        tab = self.main_window.settings_tab
        tab.settings_changed_signal.connect(self._on_settings_changed)
        tab.links_import_signal.connect(self._on_import_links)
        
        tab = self.main_window.links_tab
        tab.links_changed_signal.connect(self._on_links_changed)

        
        # Signaux du contrôleur de giveaway
        ctrl = self.giveaway_controller
        ctrl.log_signal.connect(self._on_log)
        ctrl.progress_signal.connect(self._on_progress)
        ctrl.status_signal.connect(self._on_status)
        ctrl.giveaway_status_signal.connect(self._on_giveaway_status)
        ctrl.win_signal.connect(self._on_win)
        ctrl.finished_signal.connect(self._on_finished)
        
        # Signaux du contrôleur de navigateur
        ctrl = self.browser_controller
        ctrl.log_signal.connect(self._on_log)
        ctrl.browser_ready_signal.connect(self._on_browser_ready)
        ctrl.login_status_signal.connect(self._on_login_status)
    
    def _load_links(self):
        """Charge les liens depuis le fichier de liens"""
        links = self.settings.load_links()
        self.giveaway_controller.set_links(links)
        self.main_window.links_tab.load_links(links)
        
        # Mettre à jour l'interface
        self._on_log(f"Liens chargés: {len(links)}")
    
    def _on_start_participation(self):
        """Démarre le processus de participation aux giveaways"""
        self._on_log("Démarrage de la participation aux giveaways...")
        
        # Réinitialiser la table
        self.main_window.participation_tab.table.setRowCount(0)
        
        # Vérifier si le navigateur est toujours actif ou s'il faut le réinitialiser
        if self.browser_controller.browser_model.driver:
            try:
                # Tester si la session est toujours valide
                self.browser_controller.browser_model.driver.current_url
            except Exception as e:
                self._on_log("Session de navigateur expirée, réinitialisation...")
                self.browser_controller.close_browser()
                self.browser_controller.browser_model.driver = None
        
        # Initialiser le navigateur si nécessaire
        if not self.browser_controller.browser_model.driver:
            # Récupérer le mode headless depuis les paramètres
            headless_mode = self.settings.headless_mode if hasattr(self.settings, "headless_mode") else False
            
            driver = self.browser_controller.initialize_browser(wait_page_load=False, headless_mode=headless_mode)
            if not driver:
                self._on_log("Impossible d'initialiser le navigateur")
                self.main_window.participation_tab.reset_ui()
                return
            
            # Se connecter à Instant Gaming
            if not self.browser_controller.login():
                self._on_log("Impossible de se connecter à Instant Gaming")
                self.main_window.participation_tab.reset_ui()
                return
        
        # Démarrer la participation
        wait_delay = self.settings.wait_delay
        auto_close_tabs = self.settings.auto_close_tabs
        
        if not self.giveaway_controller.start_participation(wait_delay, auto_close_tabs):
            self._on_log("Impossible de démarrer la participation")
            self.main_window.participation_tab.reset_ui()
    
    def _on_stop_participation(self):
        """Arrête le processus de participation"""
        self.giveaway_controller.stop()
    
    def _on_start_verification(self):
        """Démarre le processus de vérification des giveaways"""
        self._on_log("Démarrage de la vérification des giveaways...")
        
        # Réinitialiser la table
        self.main_window.verification_tab.table.setRowCount(0)
        
        # Vérifier si le navigateur est toujours actif ou s'il faut le réinitialiser
        if self.browser_controller.browser_model.driver:
            try:
                # Tester si la session est toujours valide
                self.browser_controller.browser_model.driver.current_url
            except Exception as e:
                self._on_log("Session de navigateur expirée, réinitialisation...")
                self.browser_controller.close_browser()
                self.browser_controller.browser_model.driver = None
        
        # Initialiser le navigateur si nécessaire
        if not self.browser_controller.browser_model.driver:
            # Récupérer le mode headless depuis les paramètres
            headless_mode = self.settings.headless_mode if hasattr(self.settings, "headless_mode") else False
            
            # Afficher un message si le mode invisible est activé
            if headless_mode:
                self._on_log("Mode invisible activé pour la vérification")
            
            driver = self.browser_controller.initialize_browser(wait_page_load=True, headless_mode=headless_mode)
            if not driver:
                self._on_log("Impossible d'initialiser le navigateur")
                self.main_window.verification_tab.reset_ui()
                return
            
            # Se connecter à Instant Gaming
            if not self.browser_controller.login():
                self._on_log("Impossible de se connecter à Instant Gaming")
                self.main_window.verification_tab.reset_ui()
                return
        
        # Démarrer la vérification
        wait_delay = self.settings.wait_delay
        
        if not self.giveaway_controller.start_verification(wait_delay):
            self._on_log("Impossible de démarrer la vérification")
            self.main_window.verification_tab.reset_ui()
    
    def _on_stop_verification(self):
        """Arrête le processus de vérification"""
        self.giveaway_controller.stop()
    
    def _on_settings_changed(self, new_settings):
        """Met à jour les paramètres de l'application"""
        self.settings.update(new_settings)
        self.settings.save()
        
        # Transmettre les paramètres mis à jour au contrôleur de navigateur
        self.browser_controller.set_settings(self.settings)
        
        # Mettre à jour l'affichage du nom d'utilisateur si nécessaire
        if "auto_detect_username" in new_settings or "username" in new_settings:
            if not self.settings.auto_detect_username and self.settings.username:
                self.main_window.verification_tab.set_username(self.settings.username)
            elif self.settings.auto_detect_username and self.settings.username and self.browser_controller.username is None:
                # Si mode auto mais pas encore connecté au navigateur, utiliser le nom des paramètres avec indication
                self.main_window.verification_tab.set_username(f"{self.settings.username} (Auto)")
            elif self.settings.auto_detect_username and self.browser_controller.username:
                # Si mode auto et déjà connecté, utiliser le nom détecté avec indication
                self.main_window.verification_tab.set_username(f"{self.browser_controller.username} (Auto)")
        
        self._on_log("Paramètres sauvegardés")
    
    def _on_links_changed(self, links):
        """Enregistre les liens modifiés"""
        self.giveaway_controller.set_links(links)
        self.settings.save_links(links)
        self._on_log(f"Liste de liens mise à jour: {len(links)} liens")

    
    def _on_import_links(self, file_path):
        """Importe des liens depuis un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                links = json.load(f)
                
            if isinstance(links, list):
                self.giveaway_controller.set_links(links)
                self.settings.save_links(links)
                self._on_log(f"Liens importés: {len(links)}")
                
                # Afficher une confirmation
                QMessageBox.information(
                    self.main_window,
                    "Import réussi",
                    f"{len(links)} liens ont été importés avec succès."
                )
            else:
                self._on_log("Format de fichier invalide")
                
                # Afficher une erreur
                QMessageBox.critical(
                    self.main_window,
                    "Erreur d'import",
                    "Format de fichier invalide."
                )
        except Exception as e:
            self._on_log(f"Erreur lors de l'import des liens: {str(e)}")
            
            # Afficher une erreur
            QMessageBox.critical(
                self.main_window,
                "Erreur d'import",
                f"Impossible d'importer les liens: {str(e)}"
            )
    
    def _on_log(self, message):
        """Gère les messages de log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Ajouter le message aux deux onglets
        self.main_window.participation_tab.add_log(formatted_message)
        self.main_window.verification_tab.add_log(formatted_message)
    
    def _on_progress(self, current, total):
        """Met à jour la barre de progression"""
        current_tab_index = self.main_window.tabs.currentIndex()
        
        if current_tab_index == 0:  # Onglet de participation
            self.main_window.participation_tab.update_progress(current, total)
        elif current_tab_index == 1:  # Onglet de vérification
            self.main_window.verification_tab.update_progress(current, total)
    
    def _on_status(self, status):
        """Met à jour le statut affiché"""
        current_tab_index = self.main_window.tabs.currentIndex()
        
        if current_tab_index == 0:  # Onglet de participation
            self.main_window.participation_tab.update_status(status)
        elif current_tab_index == 1:  # Onglet de vérification
            self.main_window.verification_tab.update_status(status)
    
    def _on_giveaway_status(self, giveaway):
        """Met à jour le statut d'un giveaway dans le tableau"""
        current_tab_index = self.main_window.tabs.currentIndex()
        
        if current_tab_index == 0:  # Onglet de participation
            # Ajouter ou mettre à jour le giveaway dans le tableau
            self._update_participation_table(giveaway)
        elif current_tab_index == 1:  # Onglet de vérification
            # Ajouter ou mettre à jour le giveaway dans le tableau
            self._update_verification_table(giveaway)
    
    def _update_participation_table(self, giveaway):
        """Met à jour le tableau de participation avec les informations du giveaway"""
        table = self.main_window.participation_tab.table
        
        # Chercher si le giveaway existe déjà dans le tableau
        found = False
        for row in range(table.rowCount()):
            if table.item(row, 1).text() == giveaway.url:
                found = True
                # Mettre à jour le statut
                table.setItem(row, 2, QTableWidgetItem(giveaway.status.value))
                # Mettre à jour la date
                if giveaway.participation_date:
                    date_str = giveaway.participation_date.strftime("%Y-%m-%d %H:%M:%S")
                    table.setItem(row, 3, QTableWidgetItem(date_str))
                break
        
        if not found:
            # Ajouter une nouvelle ligne
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            # Ajouter les informations
            table.setItem(row_position, 0, QTableWidgetItem(giveaway.influencer_name))
            table.setItem(row_position, 1, QTableWidgetItem(giveaway.url))
            table.setItem(row_position, 2, QTableWidgetItem(giveaway.status.value))
            
            if giveaway.participation_date:
                date_str = giveaway.participation_date.strftime("%Y-%m-%d %H:%M:%S")
                table.setItem(row_position, 3, QTableWidgetItem(date_str))
    
    def _update_verification_table(self, giveaway):
        """Met à jour le tableau de vérification avec les informations du giveaway"""
        table = self.main_window.verification_tab.table
        
        # Chercher si le giveaway existe déjà dans le tableau
        found = False
        for row in range(table.rowCount()):
            if table.item(row, 1).text() == giveaway.url:
                found = True
                # Mettre à jour le statut
                table.setItem(row, 2, QTableWidgetItem(giveaway.status.value))
                # Mettre à jour le gagnant
                if giveaway.winner_name:
                    table.setItem(row, 3, QTableWidgetItem(giveaway.winner_name))
                # Mettre à jour la date
                if giveaway.participation_date:
                    date_str = giveaway.participation_date.strftime("%Y-%m-%d %H:%M:%S")
                    table.setItem(row, 4, QTableWidgetItem(date_str))
                break
        
        if not found:
            # Ajouter une nouvelle ligne
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            # Ajouter les informations
            table.setItem(row_position, 0, QTableWidgetItem(giveaway.influencer_name))
            table.setItem(row_position, 1, QTableWidgetItem(giveaway.url))
            table.setItem(row_position, 2, QTableWidgetItem(giveaway.status.value))
            
            if giveaway.winner_name:
                table.setItem(row_position, 3, QTableWidgetItem(giveaway.winner_name))
            
            if giveaway.participation_date:
                date_str = giveaway.participation_date.strftime("%Y-%m-%d %H:%M:%S")
                table.setItem(row_position, 4, QTableWidgetItem(date_str))
    
    def _on_win(self, giveaway):
        """Appelé lorsqu'un giveaway a été gagné"""
        if giveaway.participation_date:
            date_str = giveaway.participation_date.strftime("%Y-%m-%d")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Ajouter le giveaway gagné au tableau des gagnants
        self.main_window.verification_tab.add_win(
            giveaway.influencer_name,
            giveaway.url,
            date_str
        )
    
    def _on_finished(self):
        """Appelé lorsque le processus est terminé"""
        current_tab_index = self.main_window.tabs.currentIndex()
        
        if current_tab_index == 0:  # Onglet de participation
            self.main_window.participation_tab.reset_ui()
        elif current_tab_index == 1:  # Onglet de vérification
            self.main_window.verification_tab.reset_ui()
    
    def _on_browser_ready(self, ready):
        """Appelé lorsque l'état du navigateur change"""
        if not ready:
            # Réinitialiser l'interface
            self.main_window.participation_tab.reset_ui()
            self.main_window.verification_tab.reset_ui()
            
            # Afficher un message d'erreur
            QMessageBox.critical(
                self.main_window,
                "Erreur de navigation",
                "Impossible d'initialiser le navigateur Chrome."
            )
    
    
    def _on_login_success(self):
        """Appelé lorsque la connexion est réussie"""
        username = self.browser_controller.username
        
        # Mettre à jour l'interface avec le nom d'utilisateur
        if username:
            # Vérifier si on est en mode auto-détection
            if self.settings.auto_detect_username:
                display_name = f"{username} (Auto)"
                self.main_window.set_status(f"Connecté en tant que {display_name}")
                self.main_window.verification_tab.set_username(display_name)
            else:
                self.main_window.set_status(f"Connecté en tant que {username}")
                self.main_window.verification_tab.set_username(username)
            
            # Log pour debug
            self._on_log(f"Connexion réussie - Username: {username}")
            
        self.main_window.update_ui_after_login()
    
    def _on_login_status(self, success):
        """Appelé lorsque le statut de connexion change"""
        if success:
            self._on_log("Connexion réussie, mise à jour de l'interface")
            
            # Récupérer le nom d'utilisateur
            username = self.browser_controller.username
            
            # Mise à jour de l'affichage selon le mode
            if self.settings.auto_detect_username and username:
                # Mode auto avec nom détecté
                self.main_window.verification_tab.set_username(f"{username} (Auto)")
            elif not self.settings.auto_detect_username and self.settings.username:
                # Mode manuel avec nom configuré
                self.main_window.verification_tab.set_username(self.settings.username)
            elif username:
                # Fallback sur le nom détecté
                self.main_window.verification_tab.set_username(username)
            else:
                # Aucun nom disponible
                self.main_window.verification_tab.set_username("Non connecté")
        else:
            self._on_log("Échec de la connexion")
            
            # En cas d'échec, afficher le nom configuré si disponible
            if not self.settings.auto_detect_username and self.settings.username:
                self.main_window.verification_tab.set_username(self.settings.username)
            elif self.settings.auto_detect_username and self.settings.username:
                self.main_window.verification_tab.set_username(f"{self.settings.username} (Auto)")
            else:
                self.main_window.verification_tab.set_username("Non connecté")
