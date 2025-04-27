from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time
from datetime import datetime
import traceback
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from src.models.giveaway import Giveaway, GiveawayStatus
from src.controllers.browser_controller import BrowserController

class GiveawayWorker(QThread):
    """Thread de travail pour participer aux giveaways"""

    progress_signal = pyqtSignal(int, int)
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    giveaway_status_signal = pyqtSignal(Giveaway)
    finished_signal = pyqtSignal()

    def __init__(self, browser_controller, links, wait_delay=0.3, auto_close_tabs=True):
        super().__init__()
        self.browser_controller = browser_controller
        self.links = links
        self.wait_delay = wait_delay
        self.auto_close_tabs = auto_close_tabs
        self.running = True

    def run(self):
        """Exécute le processus de participation aux giveaways"""
        driver = self.browser_controller.browser_model.driver
        if not driver:
            self.log_signal.emit("Erreur: Navigateur non initialisé")
            return

        total_links = len(self.links)
        nb_participated = 0
        nb_already_participated = 0
        nb_finished = 0
        nb_dead_links = 0

        for i, link in enumerate(self.links):
            if not self.running:
                break

            current = i + 1
            self.progress_signal.emit(current, total_links)
            self.status_signal.emit(f"Traitement du giveaway {current}/{total_links}")

            # Créer un objet Giveaway
            giveaway = Giveaway.from_url(link)

            try:
                # Naviguer vers le lien
                self.log_signal.emit(f"Navigation vers: {link}")
                driver.get(link)
                time.sleep(self.wait_delay)

                # Fermer les onglets supplémentaires si l'option est activée
                if self.auto_close_tabs:
                    self.browser_controller.close_extra_tabs()

                # Vérifier l'état du giveaway
                if self._is_dead_link(driver):
                    self.log_signal.emit(f"Lien mort: {giveaway.influencer_name}")
                    giveaway.status = GiveawayStatus.DEAD_LINK
                    nb_dead_links += 1

                elif self._is_finished(driver):
                    self.log_signal.emit(f"Giveaway terminé: {giveaway.influencer_name}")
                    giveaway.status = GiveawayStatus.FINISHED
                    nb_finished += 1

                elif self._is_already_participated(driver):
                    self.log_signal.emit(f"Déjà participé: {giveaway.influencer_name}")
                    giveaway.status = GiveawayStatus.PARTICIPATED
                    giveaway.participation_date = datetime.now()
                    nb_already_participated += 1

                else:
                    # Participer au giveaway
                    self.log_signal.emit(f"Participation au giveaway: {giveaway.influencer_name}")
                    if self._participate(driver):
                        self.log_signal.emit(f"Participation réussie: {giveaway.influencer_name}")
                        giveaway.status = GiveawayStatus.PARTICIPATED
                        giveaway.participation_date = datetime.now()
                        nb_participated += 1
  
                        # Cliquer sur les boutons de points bonus si disponibles
                        self._click_bonus_points(driver)
                    else:
                        self.log_signal.emit(f"Échec de participation: {giveaway.influencer_name}")
                        giveaway.status = GiveawayStatus.UNKNOWN

                # Émettre un signal avec l'état du giveaway
                self.giveaway_status_signal.emit(giveaway)

                # Petit délai avant de passer au lien suivant
                time.sleep(self.wait_delay)

            except WebDriverException as e:
                self.log_signal.emit(f"Erreur WebDriver: {str(e)}")
            except Exception as e:
                self.log_signal.emit(f"Erreur: {str(e)}")
                traceback.print_exc()

        # Récapitulatif
        summary = (
            f"Terminé !\n"
            f"Nombre de participations: {nb_participated}\n"
            f"Déjà participé: {nb_already_participated}\n"
            f"Giveaways terminés: {nb_finished}\n"
            f"Liens morts: {nb_dead_links}"
        )
        self.log_signal.emit(summary)
        self.status_signal.emit("Terminé")

        # Retour à la page d'accueil
        driver.get("https://www.instant-gaming.com/fr")

        self.finished_signal.emit()

    def stop(self):
        """Arrête le thread de travail"""
        self.running = False

    def _is_dead_link(self, driver):
        """Vérifie si le lien est mort (erreur 404)"""
        elements = driver.find_elements(By.CLASS_NAME, 'e404')
        return len(elements) > 0

    def _is_finished(self, driver):
        """Vérifie si le giveaway est terminé"""
        elements = driver.find_elements(By.XPATH, '//*[@id="giveaway-app"]/div[3]/div/div[1]/span')
        return len(elements) > 0

    def _is_already_participated(self, driver):
        """Vérifie si l'utilisateur a déjà participé au giveaway"""
        selecteur_finito = '#giveaway-app > div.participation-state.has-participation'
        selecteur_bonus = 'a.button.reward.alerts:not(.success)'

        finito = driver.find_elements(By.CSS_SELECTOR, selecteur_finito)
        bonus = driver.find_elements(By.CSS_SELECTOR, selecteur_bonus)

        return len(finito) > 0 and len(bonus) < 1

    def _participate(self, driver):
        """Participe au giveaway en cliquant sur le bouton Participer"""
        try:
            participate_button = driver.find_element(By.CSS_SELECTOR, '.button.validate')
            participate_button.click()
            time.sleep(self.wait_delay)
            return True
        except NoSuchElementException:
            return False

    def _click_bonus_points(self, driver):
        """Clic sur les boutons de points bonus"""
        try:
            bonus_buttons = driver.find_elements(By.CSS_SELECTOR, 'a.button.reward.alerts:not(.success)')
            if bonus_buttons:
                self.log_signal.emit(f"Points bonus disponibles: {len(bonus_buttons)}")

                for button in bonus_buttons:
                    button.click()
                    time.sleep(0.1)

                return True
            return False
        except NoSuchElementException:
            return False


class VerificationWorker(QThread):
    """Thread de travail pour vérifier les giveaways gagnés"""
    progress_signal = pyqtSignal(int, int)
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    giveaway_status_signal = pyqtSignal(Giveaway)
    win_signal = pyqtSignal(Giveaway)
    finished_signal = pyqtSignal()

    def __init__(self, browser_controller, links, wait_delay=0.3):
        super().__init__()
        self.browser_controller = browser_controller
        self.links = links
        self.wait_delay = wait_delay
        self.running = True

    def run(self):
        """Exécute le processus de vérification des giveaways"""
        driver = self.browser_controller.browser_model.driver
        username = self.browser_controller.username

        if not driver:
            self.log_signal.emit("Erreur: Navigateur non initialisé")
            return

        if not username:
            self.log_signal.emit("Erreur: Utilisateur non connecté")
            return

        username = username.lower()
        total_links = len(self.links)
        nb_wins = 0
        wins = []

        for i, link in enumerate(self.links):
            if not self.running:
                break

            current = i + 1
            self.progress_signal.emit(current, total_links)
            self.status_signal.emit(f"Vérification du giveaway {current}/{total_links}")

            # Créer un objet Giveaway
            giveaway = Giveaway.from_url(link)

            try:
                # Naviguer vers le lien
                self.log_signal.emit(f"Vérification de: {link}")
                driver.get(link)
                time.sleep(self.wait_delay)

                # Vérifier si le giveaway est terminé et a un gagnant
                if self._is_finished_with_winner(driver):
                    # Récupérer le nom du gagnant
                    winner_element = driver.find_element(By.CLASS_NAME, 'nickname')
                    winner_name = winner_element.text

                    giveaway.status = GiveawayStatus.FINISHED
                    giveaway.winner_name = winner_name

                    # Vérifier si le gagnant est l'utilisateur actuel
                    if winner_name.lower() == username:
                        self.log_signal.emit(f"FÉLICITATIONS! Vous avez gagné le giveaway de {giveaway.influencer_name}!")
                        nb_wins += 1
                        wins.append(giveaway)
                        self.win_signal.emit(giveaway)
                    else:
                        self.log_signal.emit(f"Le gagnant du giveaway {giveaway.influencer_name} est: {winner_name}")
                else:
                    if self._is_dead_link(driver):
                        giveaway.status = GiveawayStatus.DEAD_LINK
                        self.log_signal.emit(f"Lien mort: {giveaway.influencer_name}")
                    elif self._is_finished(driver):
                        giveaway.status = GiveawayStatus.FINISHED
                        self.log_signal.emit(f"Giveaway terminé (pas encore de gagnant): {giveaway.influencer_name}")
                    elif self._is_already_participated(driver):
                        giveaway.status = GiveawayStatus.PARTICIPATED
                        self.log_signal.emit(f"Participé: {giveaway.influencer_name}")
                    else:
                        giveaway.status = GiveawayStatus.AVAILABLE
                        self.log_signal.emit(f"Disponible: {giveaway.influencer_name}")

                # Émettre un signal avec l'état du giveaway
                self.giveaway_status_signal.emit(giveaway)

                # Petit délai avant de passer au lien suivant
                time.sleep(self.wait_delay)

            except WebDriverException as e:
                self.log_signal.emit(f"Erreur WebDriver: {str(e)}")
            except Exception as e:
                self.log_signal.emit(f"Erreur: {str(e)}")
                traceback.print_exc()

        # Récapitulatif
        if nb_wins > 0:
            win_msg = "FÉLICITATIONS! Vous avez gagné les giveaways suivants:\n"
            for win in wins:
                win_msg += f"- {win.influencer_name}: {win.url}\n"
            self.log_signal.emit(win_msg)
            self.status_signal.emit(f"Gagnés: {nb_wins}")
        else:
            self.log_signal.emit("Vous n'avez gagné aucun giveaway.")
            self.status_signal.emit("Terminé")

        # Ouvrir les giveaways gagnés dans le navigateur
        if wins:
            driver.get(wins[0].url)
            for win in wins[1:]:
                driver.execute_script(f"window.open('{win.url}', '_blank');")
    
        self.finished_signal.emit()

    def stop(self):
        """Arrête le thread de travail"""
        self.running = False

    def _is_dead_link(self, driver):
        """Vérifie si le lien est mort (erreur 404)"""
        elements = driver.find_elements(By.CLASS_NAME, 'e404')
        return len(elements) > 0

    def _is_finished(self, driver):
        """Vérifie si le giveaway est terminé"""
        elements = driver.find_elements(By.XPATH, '//*[@id="giveaway-app"]/div[3]/div/div[1]/span')
        return len(elements) > 0

    def _is_finished_with_winner(self, driver):
        """Vérifie si le giveaway est terminé et qu'un gagnant a été désigné"""
        if not self._is_finished(driver):
            return False

        try:
            driver.find_element(By.CLASS_NAME, 'nickname')
            return True
        except NoSuchElementException:
            return False

    def _is_already_participated(self, driver):
        """Vérifie si l'utilisateur a déjà participé au giveaway"""
        selecteur = '#giveaway-app > div.participation-state.has-participation'
        elements = driver.find_elements(By.CSS_SELECTOR, selecteur)
        return len(elements) > 0


class GiveawayController(QObject):
    """Contrôleur principal pour les opérations sur les giveaways"""
    # Signaux pour la communication avec l'interface utilisateur
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    status_signal = pyqtSignal(str)
    giveaway_status_signal = pyqtSignal(Giveaway)
    win_signal = pyqtSignal(Giveaway)
    finished_signal = pyqtSignal()

    def __init__(self, browser_controller: BrowserController):
        super().__init__()
        self.browser_controller = browser_controller
        self.worker = None
        self.links = []

    def set_links(self, links):
        """Définit la liste des liens de giveaway à traiter"""
        self.links = links

    def start_participation(self, wait_delay=0.3, auto_close_tabs=True):
        """Démarre le processus de participation aux giveaways"""
        if not self.browser_controller.browser_model.driver:
            self.log_signal.emit("Erreur: Navigateur non initialisé")
            return False

        if not self.links:
            self.log_signal.emit("Erreur: Aucun lien de giveaway disponible")
            return False

        # Créer et démarrer le worker
        self.worker = GiveawayWorker(
            self.browser_controller, 
            self.links,
            wait_delay=wait_delay,
            auto_close_tabs=auto_close_tabs
        )

        # Connecter les signaux
        self.worker.progress_signal.connect(self.progress_signal.emit)
        self.worker.status_signal.connect(self.status_signal.emit)
        self.worker.log_signal.connect(self.log_signal.emit)
        self.worker.giveaway_status_signal.connect(self.giveaway_status_signal.emit)
        self.worker.finished_signal.connect(self._on_worker_finished)

        # Démarrer le thread
        self.worker.start()
        return True

    def start_verification(self, wait_delay=0.3):
        """Démarre le processus de vérification des giveaways gagnés"""
        if not self.browser_controller.browser_model.driver:
            self.log_signal.emit("Erreur: Navigateur non initialisé")
            return False

        if not self.links:
            self.log_signal.emit("Erreur: Aucun lien de giveaway disponible")
            return False

        # Créer et démarrer le worker
        self.worker = VerificationWorker(
            self.browser_controller, 
            self.links,
            wait_delay=wait_delay
        )

        # Connecter les signaux
        self.worker.progress_signal.connect(self.progress_signal.emit)
        self.worker.status_signal.connect(self.status_signal.emit)
        self.worker.log_signal.connect(self.log_signal.emit)
        self.worker.giveaway_status_signal.connect(self.giveaway_status_signal.emit)
        self.worker.win_signal.connect(self.win_signal.emit)
        self.worker.finished_signal.connect(self._on_worker_finished)

        # Démarrer le thread
        self.worker.start()
        return True

    def stop(self):
        """Arrête le processus en cours"""
        if self.worker and self.worker.isRunning():
            self.log_signal.emit("Arrêt du processus...")
            self.worker.stop()
            self.worker.wait()  # Attendre que le thread se termine
            self.log_signal.emit("Processus arrêté")
            return True
        return False

    def _on_worker_finished(self):
        """Appelé lorsque le worker a terminé son travail"""
        self.finished_signal.emit()
