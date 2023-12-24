
import pandas as pd

from enum import Enum
from dataclasses import dataclass
from geographiclib.geodesic import Geodesic


class AirwayType(Enum):
    CUSTOM = 0
    DEPARTURE = 1
    ENROUTE = 2
    ARRIVAL = 3


class WaypointType(Enum):
    CUSTOM = 0
    FIX = 1
    NAVAID = 2
    AIRPORT = 3


@dataclass
class Waypoint:
    name: str = ""
    lat: float = 0.0
    lon: float = 0.0
    wpt_type: WaypointType = WaypointType.CUSTOM
    runway: str = ""


@dataclass
class Airway:
    start_pt: Waypoint = None
    end_pt: Waypoint = None
    distance: float = 0.0
    is_valid: bool = False
    airway_type: AirwayType = AirwayType.CUSTOM
    name: str = ""


class AirwayGraph:

    def __init__(self, verbose=True):
        # Geodesic setup.
        self.geod = Geodesic.WGS84

        # Flag for turning prints on and off.
        self.verbose = verbose

        # Map of waypoints and airports.
        """
        waypoints = {
            'wpt_name': Waypoint
        }
        """
        self.waypoints = {}

        # Map of airways based on fixes
        """
        airways = {
            'wpt1': {
                'wpt2': awy1, 
                'wpt3': awy2,
                ...
            },
            'wpt2': {
                'wpt1': awy1,
                'wpt3': awy3,
                ...
            },
            ...
        }
        """
        self.airways = {}

    def add_airway(self, start_wpt_id: str, end_wpt_id: Waypoint, airway_type: AirwayType, name=""):
        """
        Adds an airway (edge) to the graph. Airways are not necessarily bidirectional, so only one 
        airway is added between points.

        Arguments:
        - `start_wpt_id` (str): starting waypoint identifier for the airway
        - `end_wpt_id` (str): end waypoint identifier for the airway
        - `airway_type` (AirwayType): type of airway
        - `name` (str, optional): name of a named airway, such as a standard departure or arrival
        """
        if start_wpt_id not in self.waypoints.keys():
            if self.verbose:
                print(f"{start_wpt_id} not in waypoint list, skipping airway {start_wpt_id}->{end_wpt_id}")
            return
        elif end_wpt_id not in self.waypoints.keys():
            if self.verbose:
                print(f"{end_wpt_id} not in waypoint list, skipping airway {start_wpt_id}->{end_wpt_id}")
            return

        # Get the waypoints
        start_wpt = self.waypoints[start_wpt_id]
        end_wpt = self.waypoints[end_wpt_id]

        # Forward direction
        awy = Airway()
        awy.start_pt = start_wpt
        awy.end_pt = end_wpt
        awy.airway_type = airway_type
        awy.name = name

        # Uniqueness flag
        awy_is_unique = True

        # Ensure the airways aren't already in the graph.
        if start_wpt.name in self.airways.keys():
            if end_wpt.name in self.airways[start_wpt.name].keys():
                if self.verbose:
                    print(f"Airway {start_wpt.name}->{end_wpt.name} already exists, skipping...")
                awy_is_unique = False
        else:
            self.airways[start_wpt.name] = {}

        # Compute distance between waypoints (labeled s12 by geographiclib).
        g = self.geod.Inverse(start_wpt.lat, start_wpt.lon, end_wpt.lat, end_wpt.lon)
        awy.distance = g['s12']

        # TODO: check validity with respect to airspace, NOTAMs, etc. For now, assume the airway is valid.
        awy.is_valid = True

        # Add the airway to the airway map if it is unique.
        if awy_is_unique:
            self.airways[start_wpt.name][end_wpt.name] = awy

    def add_waypoint(self, id: str, lat: float, lon: float, wpt_type: WaypointType, rwy: str = ""):
        """
        Adds a waypoint (node) to the waypoint dictionary in the graph.

        Arguments:
        - `id` (str): waypoint identifier
        - `lat` (float): waypoint latitude in decimal degrees.
        - `lon` (float): waypoint longitude in decimal degrees.
        - `wpt_type` (WaypointType): type of waypoint
        - `rwy` (str, optional): runway name
        """
        if id in self.waypoints.keys():
            if self.verbose:
                print(f"Waypoint {id} already exists, skipping...")
            return

        wpt = Waypoint()
        wpt.lat = lat
        wpt.lon = lon
        wpt.name = id
        wpt.wpt_type = wpt_type
        wpt.runway = rwy

        # Add to the waypoint map.
        self.waypoints[wpt.name] = wpt

    def load_nasr_fixes(self, fix_file: str):
        """
        Arguments:
        - `fix_file` (str): File path for the FAA's NASR database FIX_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_fix_base_csv = pd.read_csv(fix_file)

        # Go through all fixes and generate waypoints.
        for _, row in nasr_fix_base_csv.iterrows():
            self.add_waypoint(
                row['FIX_ID'],
                row['LAT_DECIMAL'],
                row['LONG_DECIMAL'],
                WaypointType.FIX, "")

    def load_nasr_airports(self, apt_file: str):
        """
        Arguments:
        - `apt_file` (str): File path for the FAA's NASR database APT_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_apt_base_csv = pd.read_csv(apt_file)

        # Go through all fixes and generate waypoints.
        for _, row in nasr_apt_base_csv.iterrows():
            self.add_waypoint(
                row['ARPT_ID'],
                row['LAT_DECIMAL'],
                row['LONG_DECIMAL'],
                WaypointType.AIRPORT, "")

    def load_nasr_navaids(self, nav_file: str) -> None:
        """
        Arguments:
        - `nav_file` (str): File path for the FAA's NASR database NAV_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_nav_base_csv = pd.read_csv(nav_file)

        # Go through all navaids and generate waypoints.
        for _, row in nasr_nav_base_csv.iterrows():
            navaid_name = f"{row['NAV_ID']}_{row['NAME']}_{row['NAV_TYPE']}"
            self.add_waypoint(
                navaid_name,
                row['LAT_DECIMAL'],
                row['LONG_DECIMAL'],
                WaypointType.NAVAID, "")

    def load_nasr_airways(self, awy_file: str):
        """
        Generate an augmented airways database from official FAA data and GPS navaids.

        Arguments:
        - `awy_file` (str): File path for the FAA's NASR database AWY_SEG.csv
        """

        # The waypoints must be loaded before the airways.
        if len(self.waypoints.items()) == 0:
            if self.verbose:
                print(f"Error: Fixes must be non-empty prior to loading airways.\n"
                      f"Call load_nasr_fixes, load_nasr_navaids, and/or load_nasr_airports")
            raise Exception

        # Load the NASR airways.
        nasr_airways_csv = pd.read_csv(awy_file)

        # Go through each row, and construct an airway.
        for idx, row in nasr_airways_csv.iterrows():
            self.add_airway(row['SEG_VALUE'], row['NEXT_SEG'], AirwayType.ENROUTE)

    def load_nasr_stars(self, star_apt_file: str, star_rte_file: str):
        """
        Load the standard terminal arrivals (STARs) in as named airways.

        Arguments:
        - star_apt_file (str): File path for the FAA's NASR database STAR_APT.csv
        - star_rte_file (str): File path for the FAA's NASR database STAR_RTE.csv
        """
        pass

    def load_nasr_sids(self, sid_apt_file: str, sid_rte_file: str):
        """
        Load the standard instrument departure procedures (SIDs) in as named airways.

        Arguments:
        - sid_apt_file (str): File path for the FAA's NASR database DP_APT.csv
        - sid_rte_file (str): File path for the FAA's NASR database DP_RTE.csv
        """
        pass

    def build_custom_airways(self, n_fix=5):
        """
        Builds custom airways between FIX type waypoints. NAVAIDs and AIRPORTS are defined by the NASR database.

        Arguments:
        - `n_fix` (int): Number of fixes at most to connect when generating augmented airways.
        """

        # Return augmented airways
        # TODO: load in FIX_BASE.csv and create airways based on the N-closest fixes for a given fix.

    def find_best_path(self, start: Waypoint, end: Waypoint):
        # TODO: A* search.
        pass
