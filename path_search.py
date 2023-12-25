
from queue import PriorityQueue

from geographiclib.geodesic import Geodesic

from airway_graph import AirwayGraph
from map_types import AStarWaypoint


def find_best_path(graph: AirwayGraph, start_ident: str, end_ident: str, verbose=False) -> list:
    """
    Finds the best path between two identifiers in the airway graph.

    Arguments:
    - `graph` (AirwayGraph): Airway graph to search on.
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

    # If we are flying to/from the same point, short-circuit the search and just return that point.
    if start_ident == end_ident:
        return [start_ident]

    # Create a priority queue of nodes to expand.
    frontier = PriorityQueue()

    # Put the start waypoint in the frontier for expansion. Set the priority to 0 to have it be expanded first.
    p_wpt = AStarWaypoint()
    p_wpt.wpt = start_wpt
    p_wpt.g_val = 0.0
    p_wpt.priority = 0.0
    frontier.put(p_wpt)

    # Keep track of the visited waypoint g(x) scores.
    g_scores = {
        start_ident: 0.0
    }

    # Keep track of the waypoint predecessors in a dictionary.
    path_dict = {}

    # Geodesic is used for heuristic h(x) score.
    geod = Geodesic.WGS84

    # Flag for tracking if the goal was found.
    goal_found = False

    # While the frontier is non-empty and the goal waypoint hasn't been reached, expand the best point.
    while frontier.empty() is not True:
        # Get the best waypoint from the queue
        expand_pt = frontier.get()

        # Get the waypoint identifier.
        wpt_id = expand_pt.wpt.name

        # If the expanded point is the end point, we are done searching.
        if wpt_id == end_wpt.name:
            goal_found = True
            if verbose:
                print("Goal Found!")
            break

        # Print progress if requested.
        if verbose:
            print(
                f"Expanding {wpt_id} - f(x) = {expand_pt.priority}, g(x): {expand_pt.g_val}, h(x): {expand_pt.h_val}...")

        # Query the graph to see all connected points for this point.
        airways = graph.get_airways_at_waypoint(wpt_id)

        # If no airway is found, just expand the next point.
        if airways is None:
            continue

        # Add all airway end points to the frontier.
        for ident in airways.keys():
            # Create an A* point.
            astar_pt = AStarWaypoint()

            # Get the waypoint from the graph.
            astar_pt.wpt = graph.get_waypoint(ident)

            # Get distance traveled to this point
            airway_len = airways[ident].distance

            # Compute g(x) score (distance from start to current point)
            astar_pt.g_val = expand_pt.g_val + airway_len

            # Compute h(x) score (heuristic distance to go along path) using the geodesic distance
            # between points as the heuristic.
            g = geod.Inverse(astar_pt.wpt.lat, astar_pt.wpt.lon, end_wpt.lat, end_wpt.lon)
            astar_pt.h_val = g['s12']

            # Compute the expansion priority as f(x) = g(x) + h(x), i.e. the minimum total path distance.
            astar_pt.priority = astar_pt.g_val + astar_pt.h_val

            # Show the point being added to the queue if requested
            if verbose:
                print(
                    f"{wpt_id}->{ident} - f(x) = {astar_pt.priority}, g(x) = {astar_pt.g_val}, h(x) = {astar_pt.h_val}")

            # If the current point has not been visited, add its g(x) score to the g_score dictionary.
            # This only occurs when a point does not have a previous point tracked in the path dictionary,
            # so add the expansion point as the previous point.
            if ident not in g_scores.keys():
                g_scores[ident] = astar_pt.g_val
                path_dict[ident] = expand_pt

                # Add the point to the frontier since it is new.
                frontier.put(astar_pt)
            else:
                # Otherwise, check if the current previous point has a higher g(x) score than this one.
                # If it does, then we update the path dictionary to track the better route to this point
                # (via the point being expanded). Also update the g(x) dictionary to reflect the
                # improved path.
                if astar_pt.g_val < g_scores[ident]:
                    g_scores[ident] = astar_pt.g_val
                    path_dict[ident] = expand_pt

                    # Add the point to the frontier since it has been improved upon.
                    frontier.put(astar_pt)

        # Preview queue if requested
        if verbose:
            print(f"Queue size: {frontier.qsize()}")

    # If the goal was found, retrace the path.
    if goal_found:
        # Traverse the path from end to start
        prev_pt_id = end_wpt.name
        path = [prev_pt_id]
        while prev_pt_id != start_wpt.name:
            # Get the previous point.
            prev_pt = path_dict[prev_pt_id]

            # Find the previous point's ID.
            prev_pt_id = prev_pt.wpt.name

            # Add the previous point ID to the path.
            path.append(prev_pt_id)

        # Reverse the path so it's in the start->end order.
        path.reverse()

        return path

    else:
        print("No path available")
        return []
