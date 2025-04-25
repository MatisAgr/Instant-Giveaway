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
        
    def initialize_browser(self, wait_page_load=False, headless_mode=False):
        """Initialise le navigateur Chrome"""
        try:
            if self.browser_model.is_chrome_running():
                self.log_signal.emit("Chrome est déjà en cours d'exécution, fermeture...")
                self.browser_model.kill_chrome()
            
            self.log_signal.emit("Initialisation du navigateur Chrome...")
            if headless_mode:
                self.log_signal.emit("Mode invisible activé")
                
            self.browser_model.initialize_driver(wait_page_load, headless_mode)
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
        
        driver = self.browser_model.driver
        
        try:
            # Vérifier si nous sommes en mode headless
            is_headless = False
            for arg in driver.execute_script("return window.navigator.userAgent"):
                if "headless" in arg.lower():
                    is_headless = True
                    break
            
            self.log_signal.emit("Vérification de la connexion à Instant Gaming...")
            driver.get('https://www.instant-gaming.com/fr/')
            
            # Attente explicite plus longue pour le mode headless
            if is_headless:
                self.log_signal.emit("Mode headless - Attente prolongée du chargement...")
                import time
                time.sleep(5)  # Attente de 5 secondes pour s'assurer que la page est bien chargée
                
                # Capture d'écran pour déboguer en mode headless
                screenshot_path = "debug_homepage.png"
                driver.save_screenshot(screenshot_path)
                self.log_signal.emit(f"Capture d'écran de la page d'accueil enregistrée dans {screenshot_path}")
            
            # Vérifie si l'utilisateur est connecté avec plusieurs tentatives
            is_connected = False
            selectors_for_avatar = [
                '.login-container .user .avatar',
                '.user-info .avatar',
                '.user .avatar',
                '#igcNavbarRight .avatar'
            ]
            
            for selector in selectors_for_avatar:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        is_connected = True
                        break
                except Exception:
                    continue
            
            if is_connected:
                self.log_signal.emit("Déjà connecté à Instant Gaming")
                
                try:
                    # Récupérer le nom d'utilisateur
                    dashboard_element = driver.find_element(By.ID, 'user-menu-dashboard')
                    self.username = dashboard_element.get_attribute("href").split('/')[-1]
                    self.log_signal.emit(f"Connecté en tant que: {self.username}")
                except Exception as e:
                    self.log_signal.emit(f"Connecté mais impossible de récupérer le nom d'utilisateur: {str(e)}")
                
                self.login_status_signal.emit(True)
                return True
            else:
                self.log_signal.emit("Connexion requise, recherche du bouton de connexion...")
                
                # Essayer différents sélecteurs pour le bouton de connexion
                login_selectors = [
                    '.login-container .icon-user',
                    '.login-container a.connexion',
                    'a.connexion',
                    '.login-btn',
                    '#loginBtn',
                    '.user-login',
                    '.login'
                ]
                
                icon_user = None
                for selector in login_selectors:
                    try:
                        icon_user = driver.find_element(By.CSS_SELECTOR, selector)
                        if icon_user:
                            self.log_signal.emit(f"Bouton de connexion trouvé avec le sélecteur: {selector}")
                            break
                    except Exception:
                        continue
                
                if not icon_user:
                    self.log_signal.emit("Impossible de trouver le bouton de connexion")
                    
                    # Capture d'écran pour débogage
                    screenshot_path = "debug_login_failed.png"
                    driver.save_screenshot(screenshot_path)
                    self.log_signal.emit(f"Capture d'écran enregistrée dans {screenshot_path}")
                    
                    # Le mode headless n'est peut-être pas compatible avec le site
                    if is_headless:
                        self.log_signal.emit("Le mode invisible semble incompatible avec Instant Gaming. Essayez en mode normal.")
                    
                    self.login_status_signal.emit(False)
                    return False
                
                # Cliquer sur l'icône utilisateur pour ouvrir la boîte de connexion
                self.log_signal.emit("Clic sur le bouton de connexion...")
                icon_user.click()
                
                # Attendre que l'utilisateur se connecte
                self.log_signal.emit("Veuillez vous connecter à votre compte Instant Gaming...")
                self.log_signal.emit("(Vous avez 2 minutes pour vous connecter)")
                
                try:
                    wait = WebDriverWait(driver, 120)
                    wait.until(EC.invisibility_of_element_located((By.ID, 'loginbox-register')))
                    
                    # Recharger la page pour s'assurer que le statut de connexion est à jour
                    driver.get('https://www.instant-gaming.com/fr/')
                    
                    # Attendre le chargement de la page
                    time.sleep(3)
                    
                    try:
                        # Récupérer le nom d'utilisateur
                        dashboard_element = driver.find_element(By.ID, 'user-menu-dashboard')
                        self.username = dashboard_element.get_attribute("href").split('/')[-1]
                        self.log_signal.emit(f"Connecté avec succès en tant que: {self.username}")
                        self.login_status_signal.emit(True)
                        return True
                    except Exception as e:
                        self.log_signal.emit(f"Erreur lors de la récupération du nom d'utilisateur: {str(e)}")
                        # Essayer de vérifier autrement si connecté
                        for selector in selectors_for_avatar:
                            if driver.find_elements(By.CSS_SELECTOR, selector):
                                self.log_signal.emit("Connecté avec succès, mais impossible de récupérer le nom d'utilisateur")
                                self.login_status_signal.emit(True)
                                return True
                        
                        self.log_signal.emit("La connexion semble avoir échoué")
                        self.login_status_signal.emit(False)
                        return False
                
                except TimeoutException:
                    self.log_signal.emit("Échec de la connexion: délai dépassé")
                    self.login_status_signal.emit(False)
                    return False
        
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de la connexion: {str(e)}")
            
            # Capture d'écran en cas d'erreur
            try:
                screenshot_path = "login_error.png"
                driver.save_screenshot(screenshot_path)
                self.log_signal.emit(f"Capture d'écran d'erreur enregistrée dans {screenshot_path}")
            except:
                pass
                
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