
from queue import PriorityQueue

from airway_graph import AirwayGraph
from map_types import AStarWaypoint


def find_best_path(self, graph: AirwayGraph, start_ident: str, end_ident: str) -> list:
    """
    Finds the best path between two identifiers in the airway graph.

    Arguments:
    - `start_ident` (str): Named fix of the start point.
    - `end_ident` (str): Named fix of the end point.
    """
    # Load in the start and end waypoints.
    start_wpt = graph.get_waypoint(start_ident)
    end_wpt = graph.get_waypoint(end_ident)

    # Check that the provided identifiers exist.
    if start_wpt is None:
        print(
            f"Error: {start_ident} start identifier is not in the waypoints database. No path available")
        return []
    elif end_wpt is None:
        print(
            f"Error: {end_ident} end identifier is not in the waypoints database. No path available")
        return []

    # Create a priority queue of nodes to expand.
    frontier = PriorityQueue()

    # Put the start waypoint in the frontier for expansion. Set the priority to 0 to have it be expanded first.
    p_wpt = AStarWaypoint()
    p_wpt.wpt = start_wpt
    frontier.put(p_wpt)

    #
