import os
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Settings:
    """Configuration de l'application"""
    chrome_path: str = ""
    wait_delay: float = 0.3
    auto_download_driver: bool = True
    auto_close_tabs: bool = True
    retry_attempts: int = 3
    headless_mode: bool = False
    links_file_path: str = "resources/data/links.json"
    
    @classmethod
    def load(cls) -> 'Settings':
        """Charge les paramètres depuis le fichier de configuration"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'resources', 'config', 'settings.json')
        
        # Si le fichier n'existe pas, on retourne les paramètres par défaut
        if not os.path.exists(config_path):
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Chargement des paramètres: {data}")  
                return cls(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return cls()
    
    def save(self) -> None:
        """Enregistre les paramètres dans le fichier de configuration"""
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'resources', 'config')
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'settings.json')
        
        # Débogage - vérifier si headless_mode est présent
        print(f"Sauvegarde des paramètres: {asdict(self)}")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)

    def update(self, new_settings: dict) -> None:
        """Met à jour les paramètres"""
        for key, value in new_settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def load_links(self) -> List[str]:
        """Charge les liens depuis le fichier de liens"""
        links_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                self.links_file_path)
        
        try:
            with open(links_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_links(self, links: List[str]) -> None:
        """Enregistre les liens dans le fichier de liens"""
        links_dir = os.path.dirname(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            self.links_file_path
        ))
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(links_dir, exist_ok=True)
        
        links_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                self.links_file_path)
        
        with open(links_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2)