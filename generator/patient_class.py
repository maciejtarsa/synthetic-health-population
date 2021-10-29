#!/usr/bin/python3
from dataclasses import dataclass, field

@dataclass
class Patient:
    """
    A class to represent a patient.
    
    Attributes
    ----------
    id: str
    region: str
    area: str
    ethnicity: str
    gender: str
    age_range: str
    dob: str
    age: int
    deprivation_level: int
    timelines: dict (empty by default)
    """
    
    id: str
    region: str
    area: str
    ethnicity: str
    gender: str
    age_range: str
    dob: str
    age: int
    deprivation_level: int
    timelines: dict = field(default_factory=dict)
        
