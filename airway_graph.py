
import pandas as pd 

from dataclasses import dataclass


@dataclass
class Waypoint:
    name: str
    is_airport: bool
    runway: str = ""


@dataclass
class Airway:
    start_pt: Waypoint
    end_pt: Waypoint
    distance: float
    is_valid: bool


class AirwayGraph:

    def __init__(self):
        # Map of airways based on fixes
        """
        airways = {
            'wpt1': [awy1, awy2, ...],
            'wpt2': [awy1, awy2, ...],
            ...
        }
        """
        self.airways = {}
    
    def add_airway(self, awy: Airway):
        # Get the point that the airway begins at.
        start_point = awy.start_pt

        # Add the airway to the airway map.
        self.airways[start_point] = awy

    
    def load_defined_airways(self, awy_file: str):
        """
        Generate an augmented airways database from official FAA data and GPS navaids.

        Arguments:
        - awy_file (str): File path for the FAA's NASR database AWY_SEG.csv
        """

        # Load the NASR airways
        nasr_airways_csv = pd.read_csv(awy_file)

        
        # Return augmented airways
        # TODO: load in FIX_BASE.csv and create airways based on the N-closest fixes for a given fix.
        return nasr_airways_csv

    def build_custom_airways(self, fix_file: str, n_fix=5):
        """
        Arguments:
        - fix_file (str): File path for the FAA's NASR database FIX_BASE.csv
        - n_fix (int): Number of fixes at most to connect when generating augmented airways.
        """

        # Load the NASR fixes
        nasr_fix_base_csv = pd.read_csv(fix_file)

    def shortest_path(self, start: Waypoint, end: Waypoint):
        # TODO: A* search.
        pass

    