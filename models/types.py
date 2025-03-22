from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Character:
    name: str
    realName: str

@dataclass
class Team:
    name: str

@dataclass
class Gene:
    name: str

@dataclass
class Power:
    name: str

@dataclass
class DataEntry:
    character: Character
    team: Team
    genes: List[Gene]
    powers: List[Power] 