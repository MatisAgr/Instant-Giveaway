'''
Script qui vérifie si on a gagné un giveaway
'''
import os
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

import participer

PATH = participer.PATH
JSONPATH = participer.JSONPATH

# ----------------------- #
NB_GA_WIN = 0
NB_GA = 0

DATE = str(datetime.now()).split('.', maxsplit=1)[0]
LOGS = f"*{'-' * 35}*\n  Logs de vérification du {DATE} :\n"
WIN_LOGS = ''
# ----------------------- #


# -------------------------------- Utils --------------------------------- #

def search(driver, username) -> bool:
    '''
    Vérifie qui a gagné le giveaway et compare avec le nom donné
    :param driver: driver de la page
    :param username: nom de l'utilisateur
    :return: True si on a gagné, False sinon
    '''
    global NB_GA_WIN

    winnername = driver.find_element(By.CLASS_NAME,'nickname')

    if winnername.text.lower() == username:
        NB_GA_WIN += 1
        return True
    return False

def opentab(driver,lien):
    '''
    Ouvre un nouvel onglet avec le lien donné
    :param driver: driver de la page
    :param lien: lien à ouvrir
    '''
    driver.execute_script(f"window.open('{lien}','_blank');")


# ------------------------------- Console -------------------------------- #

def afficher_console_win(liste_lien):
    '''
    Affiche dans la console les liens des giveaways gagnés
    :param liste_lien: liste des liens des giveaways gagnés
    '''
    global LOGS, WIN_LOGS

    log = ''
    log += '-' * 100
    log += '\n'
    log += '\tVOUS AVEZ GAGNÉ, vérifiez vos mails'
    log += '\n'
    log += 'Voici le(s) Giveaway Gagnant(s):'
    log += '\n'
    log += '\n'

    for lien in liste_lien:
        nom = participer.getname(lien)
        logtemp = ''

        logtemp += f'Giveaway de : \t\t{nom}'
        logtemp += '\n'
        logtemp += f'Lien du giveaway : \t{lien}\n'
        logtemp += '\n'

        WIN_LOGS += logtemp
        log += logtemp

    print(log)
    LOGS += log + '\n'

def afficher_console_lose(driver, lien, show_winner=False):
    '''
    Affiche dans la console les liens des giveaways en cours de vérification
    :param lien: lien du giveaway
    :param driver: driver de la page
    '''
    global LOGS

    nom = participer.getname(lien)
    log = ''
    log += '-' * 100
    log += '\n'
    log += f'Lien n°{LINK.index(lien)+1}/{len(LINK)}\n'
    log += '\n'
    log += f'Giveaway de : \t\t{nom}'
    log += '\n'
    log += f'Lien du giveaway : \t{lien}\n'
    log += '\n'
    if show_winner:
        log += f'Gagnant du giveaway : \t{driver.find_element(By.CLASS_NAME,'nickname').text}\n'
        log += '\n'

    print(log)
    LOGS += log + '\n'


# --------------------------- Ecriture Fichier --------------------------- #

def writelogs(log):
    '''
    Ecrie les logs dans un fichier
    :param log: logs à écrire
    '''
    absolute_path = os.path.dirname(__file__)

    relative_path = f"logs\\log verification {DATE.replace(':','-')}.txt"

    full_path = os.path.join(absolute_path, relative_path)

    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(log)

def writelogs_wins(log):
    '''
    Ecrie les logs des giveaways gagnés dans un fichier
    :param log: logs à écrire
    '''
    absolute_path = os.path.dirname(__file__)
    relative_path = f"win\\lien_gagnants_{DATE.replace(':','-')}.txt"
    full_path = os.path.join(absolute_path, relative_path)

    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(log)


# ------------------------------ Main ----------------------------------- #

def main(links) -> bool:
    '''
    Vérifie si on a gagné un giveaway
    :param links: liste des liens des giveaways
    '''

    participer.kill_chrome()

    driver = participer.get_chrome_driver(False)
    driver.implicitly_wait(participer.SLEEPTIME)

    participer.ask_connexion(driver)

    username = driver.find_element(By.ID,'user-menu-dashboard').get_attribute("href").split('/')[-1]
    username = username.lower()

    win_link = []
    for lien in links:
        driver.get(lien)

        if not participer.check_status(driver, lien, 'reveal_winner'):
            afficher_console_lose(driver, lien)
            continue

        if search(driver,username):
            win_link.append(lien)
        afficher_console_lose(driver, lien, True)

    if len(win_link) == 1:
        driver.get(win_link[0])

    elif len(win_link) > 1:
        driver.get(win_link[0])
        for lien in range(1,len(win_link)):
            opentab(driver,win_link[lien])

    if win_link:
        afficher_console_win(win_link)
    else:
        print('Aucun giveaway gagné')
    return True


if __name__ == '__main__':
    LINK = participer.read_file(JSONPATH)
    NB_GA = len(LINK)

    try:
        main(LINK)
        writelogs(LOGS)
        if NB_GA_WIN > 0:
            writelogs_wins(WIN_LOGS)
        input("Appuyez sur n'importe quelle touche pour fermer cette page ")
    except WebDriverException as e:
        print(e)
        input("Erreur du Driver, programme arrêté")
