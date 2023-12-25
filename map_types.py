
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


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


@dataclass(order=True)
class AStarWaypoint:
    priority: float = field(default=np.inf, compare=True)
    g_val: float = field(default=np.inf, compare=False)
    h_val: float = field(default=np.inf, compare=False)
    wpt: Waypoint = field(default=None, compare=False)
