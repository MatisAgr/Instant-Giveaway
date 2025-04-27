import os
import shutil
import zipfile
from typing import Optional
import requests
import psutil
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class BrowserModel:
    """Gestion du navigateur Chrome pour Instant Gaming"""
    
    def __init__(self):
        self.user = os.getlogin()
        self.chrome_user_path = f"C:/Users/{self.user}/AppData/Local/Google/Chrome/User Data"
        self.driver: Optional[webdriver.Chrome] = None
        
    def is_chrome_running(self) -> bool:
        """Vérifie si Chrome est en cours d'exécution"""
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if process.info['name'] == 'chrome.exe':
                return True
        return False
    
    def kill_chrome(self) -> bool:
        """Termine tous les processus Chrome"""
        if not self.is_chrome_running():
            return True
            
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if process.info['name'] == 'chrome.exe':
                try:
                    pid = process.info['pid']
                    psutil.Process(pid).terminate()
                except psutil.NoSuchProcess:
                    pass
        return True
    
    def get_chromedriver_path(self) -> str:
        """Retourne le chemin vers chromedriver.exe"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'utils', 'chromedriver.exe')
    
    def download_chromedriver(self):
        """Télécharge et installe la dernière version de chromedriver"""
        utils_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils')
        os.makedirs(utils_dir, exist_ok=True)
        
        chromedriver_path = self.get_chromedriver_path()
        
        # Supprimer l'ancien driver s'il existe
        if os.path.exists(chromedriver_path):
            os.remove(chromedriver_path)
        
        # Télécharger la liste des versions
        response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver le lien de téléchargement pour la dernière version
        links = soup.find_all('code')
        download_link = None
        
        for link in links:
            if '/win64/chromedriver-win64' in link.text:
                download_link = link.text
                break
                
        if not download_link:
            raise Exception("Impossible de trouver le lien de téléchargement pour chromedriver")
        
        # Télécharger le zip
        zip_response = requests.get(download_link)
        zip_filename = download_link.split('/')[-1]
        zip_path = os.path.join(utils_dir, zip_filename)
        
        with open(zip_path, 'wb') as f:
            f.write(zip_response.content)
        
        # Extraire le zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(utils_dir)
            
        # Déplacer le chromedriver.exe
        extracted_dir = os.path.join(utils_dir, zip_filename.replace('.zip', ''))
        extracted_driver = os.path.join(extracted_dir, 'chromedriver.exe')
        shutil.move(extracted_driver, chromedriver_path)
        
        # Nettoyer
        os.remove(zip_path)
        shutil.rmtree(extracted_dir)
    
    def create_driver_options(self, wait_page_load: bool = False, headless_mode: bool = False) -> Options:
        """Crée et configure les options du driver Chrome"""
        options = Options()
        options.add_experimental_option('detach', True)
        options.page_load_strategy = 'eager' if wait_page_load else 'none'
        options.add_argument('--disable-extensions')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Ajouter le mode headless si activé avec des configurations améliorées
        if headless_mode:
            # Configuration avancée pour éviter la détection du mode headless
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Résoudre les problèmes de WebGL
            options.add_argument('--enable-unsafe-swiftshader')
            options.add_argument('--enable-swiftshader-webgl')
            
            # Ajouter des en-têtes pour simuler un vrai navigateur
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.115 Safari/537.36')
        
        # Ajouter le chemin du profil utilisateur après les options headless
        options.add_argument(f'--user-data-dir={self.chrome_user_path}')
        
        return options


    def initialize_driver(self, wait_page_load: bool = False, headless_mode: bool = False) -> webdriver.Chrome:
        """Initialise et retourne un driver Chrome configuré"""
        try:
            chromedriver_path = self.get_chromedriver_path()
            service = Service(chromedriver_path)
            options = self.create_driver_options(wait_page_load, headless_mode)
            self.driver = webdriver.Chrome(service=service, options=options)
            return self.driver
        except Exception:
            # Si le driver n'est pas trouvé, on le télécharge
            self.download_chromedriver()
            service = Service(self.get_chromedriver_path())
            options = self.create_driver_options(wait_page_load, headless_mode)
            self.driver = webdriver.Chrome(service=service, options=options)
            return self.driver


    def close_driver(self):
        """Ferme le driver Chrome"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
