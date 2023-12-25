import numpy as np
import pandas as pd

from geographiclib.geodesic import Geodesic

from map_types import Airway, AirwayType, Waypoint, WaypointType


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
        Adds an airway (edge) to the graph. Airways are bidirectional, so two airways are added between
        the provided points.

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
        fwd_awy = Airway()
        fwd_awy.start_pt = start_wpt
        fwd_awy.end_pt = end_wpt
        fwd_awy.airway_type = airway_type
        fwd_awy.name = name

        # Reverse direction
        rev_awy = Airway()
        rev_awy.start_pt = start_wpt
        rev_awy.end_pt = end_wpt
        rev_awy.airway_type = airway_type
        rev_awy.name = name

        # Uniqueness flag
        fwd_awy_is_unique = True
        rev_awy_is_unique = True

        # Ensure the airways aren't already in the graph.
        if start_wpt.name in self.airways.keys():
            if end_wpt.name in self.airways[start_wpt.name].keys():
                if self.verbose:
                    print(f"Airway {start_wpt.name}->{end_wpt.name} already exists, skipping...")
                fwd_awy_is_unique = False
        else:
            self.airways[start_wpt.name] = {}

        # Reverse direction
        if end_wpt.name in self.airways.keys():
            if start_wpt.name in self.airways[end_wpt.name].keys():
                if self.verbose:
                    print(f"Airway {end_wpt.name}->{start_wpt.name} already exists, skipping...")
                rev_awy_is_unique = False
        else:
            self.airways[end_wpt.name] = {}

        # Compute distance between waypoints (labeled s12 by geographiclib).
        g = self.geod.Inverse(start_wpt.lat, start_wpt.lon, end_wpt.lat, end_wpt.lon)
        fwd_awy.distance = g["s12"]
        rev_awy.distance = g["s12"]

        # TODO: check validity with respect to airspace, NOTAMs, etc. For now, assume the airway is valid.
        fwd_awy.is_valid = True
        rev_awy.is_valid = True

        # Add the airways to the airway map if they are unique.
        if fwd_awy_is_unique:
            self.airways[start_wpt.name][end_wpt.name] = fwd_awy
        if rev_awy_is_unique:
            self.airways[end_wpt.name][start_wpt.name] = rev_awy

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

    def load_nasr_data(self, fix_file: str, apt_file: str, navaid_file: str, awy_file: str, star_rte_file: str, sid_rte_file: str):
        """
        Loads all NASR data into the airway graph.

        Arguments:
        - `fix_file`: FIX_BASE.csv from NASR subscription
        - `apt_file`: APT_BASE.csv from NASR subscription
        - `navaid_file`: NAV_BASE.csv from NASR subscription
        - `awy_file`: AWY_SEG.csv from NASR subscription
        - `star_rte_file`: STAR_RTE.csv from NASR subscription
        - `sid_rte_file`: DP_RTE.csv from NASR subscription
        """
        # 1. Load the NASR fixes into the graph.
        self.load_nasr_fixes(fix_file)

        # 2. Load the NASR airports into the graph.
        self.load_nasr_airports(apt_file)

        # 3. Load the NASR navaids into the graph. This is done after loading airports and GPS fixes
        # in order to ensure the NAVAIDs can be deconflicted as needed with the airports and fixes.
        self.load_nasr_navaids(navaid_file)

        # 4. Load standard arrivals
        self.load_nasr_stars(star_rte_file)

        # 5. Load standard departures
        self.load_nasr_sids(sid_rte_file)

        # 6. Load all generic airways. This is done after arrivals and departures to ensure the named
        # routes get added correctly.
        self.load_nasr_airways(awy_file)

    def load_nasr_fixes(self, fix_file: str):
        """
        Loads the NASR fixes into the waypoint dictionary. These are used later when determining airway information.

        Arguments:
        - `fix_file` (str): File path for the FAA's NASR database FIX_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_fix_base_csv = pd.read_csv(fix_file)

        # Go through all fixes and generate waypoints.
        for _, row in nasr_fix_base_csv.iterrows():
            self.add_waypoint(
                row["FIX_ID"],
                row["LAT_DECIMAL"],
                row["LONG_DECIMAL"],
                WaypointType.FIX,
                "")

    def load_nasr_airports(self, apt_file: str):
        """
        Loads NASR airports into the waypoint dictionary. These are used later to define airways.

        Arguments:
        - `apt_file` (str): File path for the FAA's NASR database APT_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_apt_base_csv = pd.read_csv(apt_file)

        # Go through all fixes and generate waypoints.
        for _, row in nasr_apt_base_csv.iterrows():
            self.add_waypoint(
                row["ARPT_ID"],
                row["LAT_DECIMAL"],
                row["LONG_DECIMAL"],
                WaypointType.AIRPORT,
                "")

    def load_nasr_navaids(self, nav_file: str) -> None:
        """
        Loads NASR navaids into the waypoint dictionary. These are used later to define airways.

        Arguments:
        - `nav_file` (str): File path for the FAA's NASR database NAV_BASE.csv
        """

        # Load the NASR fixes from the CSV.
        nasr_nav_base_csv = pd.read_csv(nav_file)

        # Go through all navaids and generate waypoints.
        for _, row in nasr_nav_base_csv.iterrows():
            navaid_name = row['NAV_ID']

            # If the navaid already exists, add additional name qualifiers to differentiate this navaid.
            if navaid_name in self.waypoints.keys():
                navaid_name = f"{row['NAV_ID']}_{row['NAME']}_{row['NAV_TYPE']}"

            self.add_waypoint(
                navaid_name,
                row["LAT_DECIMAL"],
                row["LONG_DECIMAL"],
                WaypointType.NAVAID,
                "")

    def load_nasr_airways(self, awy_file: str):
        """
        Generate an augmented airways database from official FAA data and GPS navaids.

        Arguments:
        - `awy_file` (str): File path for the FAA's NASR database AWY_SEG.csv
        """

        # Waypoints must be loaded before the airways.
        if len(self.waypoints.items()) == 0:
            if self.verbose:
                print(
                    f"Error: Fixes must be non-empty prior to loading airways.\n"
                    f"Call load_nasr_fixes, load_nasr_navaids, and/or load_nasr_airports")
            raise Exception

        # Load the NASR airways.
        nasr_airways_csv = pd.read_csv(awy_file)

        # Go through each row, and construct an airway.
        for idx, row in nasr_airways_csv.iterrows():
            if np.nan not in (row["SEG_VALUE"], row["NEXT_SEG"]):
                self.add_airway(row["SEG_VALUE"], row["NEXT_SEG"], AirwayType.ENROUTE)

    def load_nasr_stars(self, star_rte_file: str):
        """
        Load the standard terminal arrivals (STARs) in as named airways.

        Arguments:
        - star_rte_file (str): File path for the FAA's NASR database STAR_RTE.csv
        """
        # Load the NASR STAR routes CSV.
        nasr_star_rte_csv = pd.read_csv(star_rte_file)

        # Go through each route and add it in as an ARRIVAL airway
        for _, row in nasr_star_rte_csv.iterrows():
            if np.nan not in (row["POINT"], row["NEXT_POINT"]):
                self.add_airway(row["POINT"], row["NEXT_POINT"],
                                AirwayType.ARRIVAL, row['ROUTE_NAME'])

    def load_nasr_sids(self, sid_rte_file: str):
        """
        Load the standard instrument departure procedures (SIDs) in as named airways.

        Arguments:
        - sid_rte_file (str): File path for the FAA's NASR database DP_RTE.csv
        """
        # Load the NASR standard departure routes CSV.
        nasr_sid_rte_csv = pd.read_csv(sid_rte_file)

        # Go through each route and add it in as an ARRIVAL airway
        for _, row in nasr_sid_rte_csv.iterrows():
            if np.nan not in (row["POINT"], row["NEXT_POINT"]):
                self.add_airway(row["POINT"], row["NEXT_POINT"],
                                AirwayType.DEPARTURE, row['DP_NAME'])

    def build_custom_airways(self, n_fix=5):
        """
        Builds custom airways between FIX type waypoints. NAVAIDs and AIRPORTS are defined by the NASR database.

        Arguments:
        - `n_fix` (int): Number of fixes at most to connect when generating augmented airways.
        """

        # Return augmented airways
        # TODO: load in FIX_BASE.csv and create airways based on the N-closest fixes for a given fix.
        pass

    def get_waypoint(self, ident: str) -> Waypoint:
        """
        Get a named waypoint from the waypoint dictionary.

        Arguments:
        - `ident` (str): The waypoint name to get.

        Returns: 
        A `Waypoint` from the waypoint dictionary with the specified name if it exists, else `None`
        """
        if ident not in self.waypoints.keys():
            if self.verbose:
                print(
                    f"Error: {ident} is not in the waypoints dictionary. No waypoint available")
            return None

        return self.waypoints[ident]

    def get_airways_at_waypoint(self, ident: str) -> dict:
        if ident not in self.airways.keys():
            if self.verbose:
                print(
                    f"Error: {ident} is not in the airways dictionary. No airways available")
            return None

        return self.airways[ident]
