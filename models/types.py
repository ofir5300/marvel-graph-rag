from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DataEntry:
    character: str
    team: str
    gene: str
    power: str