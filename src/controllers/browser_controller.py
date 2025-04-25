from PyQt6.QtCore import QObject, pyqtSignal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.models.browser import BrowserModel

class BrowserController(QObject):
    """Contrôleur pour les opérations liées au navigateur"""
    
    log_signal = pyqtSignal(str)
    browser_ready_signal = pyqtSignal(bool)
    login_status_signal = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.browser_model = BrowserModel()
        self.username = None
        
    def initialize_browser(self, wait_page_load=False):
        """Initialise le navigateur Chrome"""
        try:
            if self.browser_model.is_chrome_running():
                self.log_signal.emit("Chrome est déjà en cours d'exécution, fermeture...")
                self.browser_model.kill_chrome()
            
            self.log_signal.emit("Initialisation du navigateur Chrome...")
            self.browser_model.initialize_driver(wait_page_load)
            self.browser_ready_signal.emit(True)
            
            return self.browser_model.driver
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de l'initialisation du navigateur: {str(e)}")
            self.browser_ready_signal.emit(False)
            return None
    
    def close_browser(self):
        """Ferme le navigateur Chrome"""
        try:
            self.log_signal.emit("Fermeture du navigateur...")
            self.browser_model.close_driver()
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de la fermeture du navigateur: {str(e)}")
    
    def login(self):
        """Demande à l'utilisateur de se connecter à son compte Instant Gaming"""
        if not self.browser_model.driver:
            self.log_signal.emit("Erreur: Le navigateur n'est pas initialisé")
            return False
        
        try:
            driver = self.browser_model.driver
            
            self.log_signal.emit("Vérification de la connexion à Instant Gaming...")
            driver.get('https://www.instant-gaming.com/fr/')
            
            # Vérifie si l'utilisateur est connecté
            elements = driver.find_elements(By.CSS_SELECTOR, '.login-container .user .avatar')
            
            if elements:
                self.log_signal.emit("Déjà connecté à Instant Gaming")
                
                # Récupérer le nom d'utilisateur
                self.username = driver.find_element(By.ID, 'user-menu-dashboard').get_attribute("href").split('/')[-1]
                self.log_signal.emit(f"Connecté en tant que: {self.username}")
                
                self.login_status_signal.emit(True)
                return True
            else:
                self.log_signal.emit("Connexion requise, cliquez sur l'icône utilisateur...")
                
                # Cliquer sur l'icône utilisateur pour ouvrir la boîte de connexion
                icon_user = driver.find_element(By.CSS_SELECTOR, '.login-container .icon-user')
                icon_user.click()
                
                # Attendre que l'utilisateur se connecte
                self.log_signal.emit("Veuillez vous connecter à votre compte Instant Gaming...")
                self.log_signal.emit("(Vous avez 2 minutes pour vous connecter)")
                
                try:
                    wait = WebDriverWait(driver, 120)
                    wait.until(EC.invisibility_of_element_located((By.ID, 'loginbox-register')))
                    
                    # Récupérer le nom d'utilisateur
                    driver.get('https://www.instant-gaming.com/fr/')
                    self.username = driver.find_element(By.ID, 'user-menu-dashboard').get_attribute("href").split('/')[-1]
                    
                    self.log_signal.emit(f"Connecté avec succès en tant que: {self.username}")
                    self.login_status_signal.emit(True)
                    return True
                
                except TimeoutException:
                    self.log_signal.emit("Échec de la connexion: délai dépassé")
                    self.login_status_signal.emit(False)
                    return False
        
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de la connexion: {str(e)}")
            self.login_status_signal.emit(False)
            return False
    
    def close_extra_tabs(self):
        """Ferme tous les onglets sauf l'onglet principal"""
        if not self.browser_model.driver:
            return False
        
        try:
            driver = self.browser_model.driver
            current_handle = driver.current_window_handle
            
            # Fermer tous les autres onglets
            for handle in driver.window_handles:
                if handle != current_handle:
                    driver.switch_to.window(handle)
                    driver.close()
            
            # Revenir à l'onglet principal
            driver.switch_to.window(current_handle)
            return True
        
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de la fermeture des onglets: {str(e)}")
            return False
    
    def get_username(self):
        """Retourne le nom d'utilisateur connecté"""
        return self.username