'''
Participe à tous les giveaways disponibles dans le fichier links.json
'''
import os
import shutil
import sys
import json
import zipfile
from time import sleep
from datetime import datetime
import psutil
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, NoSuchDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Changer cette valeur si votre connexion est lente
SLEEPTIME = 0.3 # en seconde

USER = os.getlogin()
PATH = f"C:/Users/{USER}/AppData/Local/Google/Chrome/User Data"

JSONPATH = '../resources/data/links.json'

# ----------------------- #
NB_LIEN_404 = 0
NB_LIEN_DEJA_PARTICIPER = 0
NB_LIEN_FINI = 0

NB_GA_PARTICIPER = 0

LOGS = f"*{'-' * 35}*\n  Logs du {str(datetime.now()).split('.', maxsplit=1)[0]} :\n"
# ----------------------- #

# ------------------------------- Utils -------------------------------- #

def send_to_console(message):
    '''
    Envoie un message à la console js
    '''
    print(json.dumps({'message': message}))
    sys.stdout.flush()

def check_status(driver: webdriver, lien: str, wanted_state: str = 'can_particip') -> bool:
    '''
    Check l'état de la page
    '''
    if wanted_state == 'can_particip':
        if already_finish(driver) or already_participate(driver) or dead_link(driver):
            afficher_console(lien)
            return True
    elif wanted_state == 'reveal_winner':
        if already_finish(driver):
            try:
                driver.find_element(By.CLASS_NAME,'nickname')
                return True
            except NoSuchElementException:
                return False
    return False

def ask_connexion(driver: webdriver):
    '''
    Demande à l'utilisateur de se connecter à son compte IG si il ne l'est pas déjà
    :param driver: driver en cours
    '''
    driver.get('https://www.instant-gaming.com/fr/')

    element = driver.find_elements(By.CSS_SELECTOR, '.login-container .user .avatar')
    check_already_connect = element != []
    if check_already_connect:
        return
    icon_user = driver.find_element(By.CSS_SELECTOR, '.login-container .icon-user')
    icon_user.click()

    try:
        wait = WebDriverWait(driver, 120)
        element = wait.until(EC.invisibility_of_element_located((By.ID, 'loginbox-register')))
    except TimeoutException:
        print('Connectez-vous à votre compte IG et appuyez sur entrée')
        input()
    print('Compte connecté')
    return

def is_chrome_running() -> bool:
    '''
    Vériie si chrome est déjà ouvert
    :return: True si il est ouvert, False sinon
    '''
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            return True
    return False

def kill_chrome() -> bool:
    '''
    Permet de tuer tous les processus 'chrome.exe', retourne Vrai
    '''
    if not is_chrome_running():
        print("Chrome n'est pas ouvert, lancement du navigateur.")
        return True

    print('Fermeture de Chrome.')
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            try:
                pid = process.info['pid']
                psutil.Process(pid).terminate()
            except psutil.NoSuchProcess:
                print(f'Impossible de tuer le processus Chrome avec PID {pid}.')

    print('Chrome fermé, lancement du navigateur')
    return True

def read_file(fichier: str) -> list:
    '''
    Lit le fichier links.json et renvoie une liste des liens
    :return: liste des liens
    '''
    absolute_path = os.path.dirname(__file__)
    full_path = os.path.join(absolute_path, fichier)


    with open(full_path, 'r', encoding='utf-8') as f:
        if full_path.endswith('.json'):
            data = json.load(f)
        else:
            data = f.read()
        return data


# ------------------------------- Driver -------------------------------- #


def get_chrome_driver(wait_page_load: bool) -> webdriver:
    '''
    Créé et renvoie le driver
    :param wait_page_load: si il faut attendre le chargement de la page
    :return: driver
    '''
    try:
        driver = webdriver.Chrome(service=driver_service(), options=driver_options(wait_page_load))
    except NoSuchDriverException:
        telecharger_chromedriver()
        driver = webdriver.Chrome(service=driver_service(), options=driver_options(wait_page_load))
    return driver

def driver_options(wait_page_load: bool) -> Options:
    '''
    Créé et renvoie les options à appliquer au driver
    '''
    # Créez des options pour le profil Chrome
    chrome_options = Options()

    # Ne ferme pas chrome à la fin du script
    chrome_options.add_experimental_option('detach', True)

    chrome_options.page_load_strategy = 'none' if not wait_page_load else 'eager'
    chrome_options.add_argument('--disable-extensions')

    # Désactive les logs
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Ouvre chrome avec un profil
    chrome_options.add_argument(f'--user-data-dir={PATH}')

    # Spécifiez le chemin vers le binaire Chrome (facultatif)
    # chrome_options.binary_location = '/chemin/vers/chrome.exe'

    return chrome_options

def driver_service() -> webdriver.ChromeService:
    '''
    Créé et renvoie le service à appliquer au driver
    '''
    absolute_path = os.path.dirname(__file__)
    relative_path = 'utils/chromedriver.exe'
    full_path = os.path.join(absolute_path, relative_path)
    service = webdriver.ChromeService(full_path)
    return service

def telecharger_chromedriver():
    '''
    Télécharge et installe le chromedriver.exe
    '''
    absolute_path = os.path.dirname(__file__)
    fichierdriver = 'utils'
    relative_path = fichierdriver + '/chromedriver.exe'
    full_path = os.path.join(absolute_path, relative_path)
    if os.path.exists(full_path):
        print('Chromedriver.exe déjà installé')
        os.remove(full_path)
        print('Chromedriver.exe supprimé')
        print('Téléchargement de la dernière version de chromedriver.exe')
    reponse = requests.get('https://googlechromelabs.github.io/chrome-for-testing/', timeout=5)
    soup = BeautifulSoup(reponse.text, 'html.parser')
    liens = soup.find_all('code')
    for lien in liens:
        if '/win64/chromedriver-win64' in lien.text:
            lien = lien.text
            break
    fichierzip = requests.get(lien, timeout=5)
    nomfichier = lien.split('/')[-1]

    absolute_path = os.path.dirname(__file__)
    relative_path = fichierdriver + '/' + nomfichier
    full_path = os.path.join(absolute_path, relative_path)
    with open(full_path, 'wb') as f:
        f.write(fichierzip.content)
        with zipfile.ZipFile(full_path, 'r') as zip_ref:
            zip_ref.extractall(absolute_path + '/' + fichierdriver)
            shutil.move(absolute_path + '/' + fichierdriver + '/' + nomfichier.replace('.zip', '') + '' + '/chromedriver.exe', \
                        absolute_path + '/' + fichierdriver)
            zip_ref.close()
        f.close()
    os.remove(full_path)
    shutil.rmtree(absolute_path + '/' + fichierdriver + '/' + nomfichier.replace('.zip', ''))
    print('Chromedriver.exe téléchargé et installé')


# ------------------------------- Check -------------------------------- #

def already_finish(driver) -> bool:
    '''
    Vérifie si le giveaway est fini

    Renvoie True si il est fini
    False sinon
    '''
    global NB_LIEN_FINI

    finito = driver.find_elements(By.XPATH, '//*[@id="giveaway-app"]/div[3]/div/div[1]/span')
    if len(finito) == 0:
        return False

    NB_LIEN_FINI += 1
    return True

def already_participate(driver) -> bool:
    '''
    Vérifie si on a déjà participer au giveaway

    Renvoie True si on participe déjà
    False sinon
    '''
    global NB_LIEN_DEJA_PARTICIPER

    selecteur_finito = '#giveaway-app > div.participation-state.has-participation'
    selecteur_bonus = 'a.button.reward.alerts:not(.success)'

    finito = driver.find_elements(By.CSS_SELECTOR, selecteur_finito)
    bonus = driver.find_elements(By.CSS_SELECTOR, selecteur_bonus)
    if len(finito) > 0 and len(bonus) < 1:
        NB_LIEN_DEJA_PARTICIPER += 1
        return True
    return False  

# Lien 404
def dead_link(driver) -> bool:
    '''
    Vérifie si un lien est mort

    Renvoie True si il l'est
    False sinon
    '''
    global NB_LIEN_404

    finito = driver.find_elements(By.CLASS_NAME, 'e404')
    if len(finito) == 0:
        return False

    NB_LIEN_404 += 1
    return True


# ------------------------------- Click -------------------------------- #

def click_participer(driver) -> bool:
    '''
    Essaye de trouver le boutton 'Participer'
    '''
    global NB_GA_PARTICIPER

    try:
        particip = driver.find_element(By.CSS_SELECTOR, '.button.validate')
        particip.click()

        NB_GA_PARTICIPER += 1
        return True

    except NoSuchElementException:
        pass
    return False

def click_point(driver) -> bool:
    '''
    Essaye de trouver les bouttons de points
    '''
    try:
        if len(driver.find_elements(By.CSS_SELECTOR, 'a.button.reward.alerts:not(.success)')) > 0:
            elements = driver.find_elements(By.CSS_SELECTOR, 'a.button.reward.alerts:not(.success)')

            for i in elements:
                i.click()
                sleep(0.1)

            return True
    except NoSuchElementException:
        pass
    return False

def close_extra_tab(driver, page_ig) -> bool:
    '''
    Ferme les onglets en trop
    :param driver: driver en cours
    :param pageIG: la page du giveaway
    :return: True si il y a eu un changement de page
    '''
    try:
        windows = driver.window_handles
        for i in windows:
            if i != page_ig:
                driver.switch_to.window(i)
                driver.close()
        driver.switch_to.window(page_ig)
        return True
    except WebDriverException:
        pass
    return False

# ------------------------------- Affichage -------------------------------- #

def getname(lien: str) -> str:
    '''
    Donne le nom du giveaway à partir du lien
    :param lien: lien du giveaway
    :return: nom du giveaway
    '''
    txt = lien.split('/')
    return txt[len(txt)-1]

def afficher_console(lien: str):
    '''
    Affiche les logs dans la console
    et les ajoute à la variable LOGS
    :param lien: lien du giveaway
    '''
    global LOGS

    nom = getname(lien)
    log = ''
    log += '-' * 100
    log += '\n'
    log += f'Lien n°{LINK.index(lien)+1}/{len(LINK)}'
    log += '\n'
    log += f'Giveaway de : \t\t{nom}'
    log += '\n'
    log += f'Lien du giveaway : \t{lien}\n'
    log += '\n'

    log += f'Nombre de participations à un GA : {NB_GA_PARTICIPER}'
    log += '\n'
    log += f'Nombre de GA finis : {NB_LIEN_FINI}'
    log += '\n'
    log += f'Nombre de GA où vous étiez déjà : {NB_LIEN_DEJA_PARTICIPER}'
    log += '\n'
    log += f'Nombre de liens 404 : \t{NB_LIEN_404}'
    print(log)
    LOGS += log + '\n'

def writelogs(log: str):
    '''
    Ecrit les logs dans un fichier
    :param log: logs à écrire
    '''
    absolute_path = os.path.dirname(__file__)

    date = str(datetime.now()).replace(':','-').split('.', maxsplit=1)[0]
    relative_path = f'logs\\log_{date}.txt'

    full_path = os.path.join(absolute_path, relative_path)

    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(log)


# ------------------------------- Main -------------------------------- #

def main(links: list) -> bool:
    '''
    Parcours la liste des GA et participe à ceux disponible
    '''
    kill_chrome()

    driver = get_chrome_driver(False)
    driver.implicitly_wait(SLEEPTIME)

    ask_connexion(driver)

    for lien in links:
        driver.get(lien)
        page_ig = driver.current_window_handle
        close_extra_tab(driver,page_ig)

        if check_status(driver, lien, 'can_particip'):
            afficher_console(lien)
            continue

        click_participer(driver)

        click_point(driver)

        afficher_console(lien)

    driver.get('https://www.instant-gaming.com/fr')
    return True

if __name__ == '__main__':
    LINK = read_file(JSONPATH)
    try:
        main(LINK)
        writelogs(LOGS)
        if NB_GA_PARTICIPER > 0:
            print(f'\nVous avez participé à {NB_GA_PARTICIPER} giveaways, Bonne chance !')
        elif NB_LIEN_DEJA_PARTICIPER > 0:
            print("\nVous n'avez participé à aucun giveaway.")
            print(f'Vous avez déjà participé à tous les giveaways disponibles ({NB_LIEN_DEJA_PARTICIPER}).')
        input("Appuyez sur n'importe quelle touche pour fermer cette page ")
    except WebDriverException as e:
        print(e)
        print("Erreur du Driver, programme arrêté")
