from dataclasses import dataclass
from typing import List, Dict


@dataclass
class RelationalDataEntry:
    character: str
    team: str
    gene: str
    power: str

@dataclass
class InformationDataEntry:
    character: str
    text: str