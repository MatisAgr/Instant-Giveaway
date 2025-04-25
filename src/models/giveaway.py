from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class GiveawayStatus(Enum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    PARTICIPATED = "participated"
    FINISHED = "finished"
    DEAD_LINK = "dead_link"

@dataclass
class Giveaway:
    """Représentation d'un giveaway Instant Gaming"""
    url: str
    influencer_name: str
    status: GiveawayStatus = GiveawayStatus.UNKNOWN
    winner_name: Optional[str] = None
    participation_date: Optional[datetime] = None
    
    @property
    def is_available(self) -> bool:
        return self.status == GiveawayStatus.AVAILABLE
    
    @property
    def is_participated(self) -> bool:
        return self.status == GiveawayStatus.PARTICIPATED
    
    @property
    def is_finished(self) -> bool:
        return self.status == GiveawayStatus.FINISHED
    
    @property
    def is_dead_link(self) -> bool:
        return self.status == GiveawayStatus.DEAD_LINK
    
    @classmethod
    def from_url(cls, url: str) -> 'Giveaway':
        """Crée un objet Giveaway à partir d'une URL"""
        influencer_name = url.split('/')[-1]
        return cls(url=url, influencer_name=influencer_name)