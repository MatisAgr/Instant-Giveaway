from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

def is_element_present(driver, by, value, timeout=0) -> bool:
    """
    Vérifie si un élément est présent sur la page
    
    Args:
        driver: Le driver Selenium
        by: La méthode de localisation (By.ID, By.CLASS_NAME, etc.)
        value: La valeur à rechercher
        timeout: Le temps d'attente avant de considérer que l'élément n'est pas présent
        
    Returns:
        True si l'élément est présent, False sinon
    """
    try:
        if timeout > 0:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        else:
            driver.find_element(by, value)
        return True
    except (NoSuchElementException, TimeoutException):
        return False

def wait_for_element(driver, by, value, timeout=10) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Attend qu'un élément soit présent sur la page
    
    Args:
        driver: Le driver Selenium
        by: La méthode de localisation (By.ID, By.CLASS_NAME, etc.)
        value: La valeur à rechercher
        timeout: Le temps d'attente maximum en secondes
        
    Returns:
        L'élément trouvé ou None si l'élément n'est pas trouvé
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def wait_for_clickable(driver, by, value, timeout=10) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Attend qu'un élément soit cliquable sur la page
    
    Args:
        driver: Le driver Selenium
        by: La méthode de localisation (By.ID, By.CLASS_NAME, etc.)
        value: La valeur à rechercher
        timeout: Le temps d'attente maximum en secondes
        
    Returns:
        L'élément trouvé ou None si l'élément n'est pas trouvé ou n'est pas cliquable
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None

def get_elements_or_empty(driver, by, value) -> List[webdriver.remote.webelement.WebElement]:
    """
    Récupère les éléments correspondant au sélecteur ou une liste vide
    
    Args:
        driver: Le driver Selenium
        by: La méthode de localisation (By.ID, By.CLASS_NAME, etc.)
        value: La valeur à rechercher
        
    Returns:
        Liste des éléments trouvés ou liste vide si aucun élément n'est trouvé
    """
    try:
        return driver.find_elements(by, value)
    except NoSuchElementException:
        return []

def safe_click(element) -> bool:
    """
    Clique sur un élément de manière sécurisée
    
    Args:
        element: L'élément à cliquer
        
    Returns:
        True si le clic a réussi, False sinon
    """
    try:
        element.click()
        return True
    except (ElementClickInterceptedException, StaleElementReferenceException):
        return False

def scroll_to_element(driver, element):
    """
    Fait défiler la page jusqu'à l'élément
    
    Args:
        driver: Le driver Selenium
        element: L'élément jusqu'auquel faire défiler
    """
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def wait_page_load(driver, timeout=30):
    """
    Attend que la page soit complètement chargée
    
    Args:
        driver: Le driver Selenium
        timeout: Le temps d'attente maximum en secondes
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )