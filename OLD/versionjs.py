'''
Permet de participer à des giveaways mais par injection de code javascript
'''
from time import sleep
import selenium.common.exceptions as sel_excep

import participer

DELAIS = 0.5

def main(js: str):
    '''
    Fonction principale
    '''
    participer.kill_chrome()
    driver_connexion = participer.get_chrome_driver(True)
    participer.ask_connexion(driver_connexion)
    driver_connexion.quit()

    participer.kill_chrome()
    driver = participer.get_chrome_driver(False) # False

    liens = participer.read_file(participer.JSONPATH)

    num = 1
    for lien in liens:
        driver.get(lien)
        print(f"Participation au giveaway: {lien}")
        print(f"Nombre de participations: {str(num)}/{str(len(liens))}")
        print('-' * 100)
        num += 1
        if driver.execute_script(js):
            sleep(DELAIS)
            driver.execute_script(js)
            continue
        participer.close_extra_tab(driver,lien)
        sleep(DELAIS)
    driver.get("https://www.instant-gaming.com/fr")

if __name__ == '__main__':
    codejs = participer.read_file('injection.js')
    try:
        main(codejs)
    except sel_excep.WebDriverException as e:
        print(e)
        print("Erreur du Driver, programme arrêté")
