
import argparse
import pickle

from path_search import find_best_path

if __name__ == "__main__":
    # Configurable parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("start_point")
    parser.add_argument("end_point")
    parser.add_argument("--graph_file", default="data/airway_graph.pkl")

    # Parse the arguments
    args = parser.parse_args()
    start_id = args.start_point
    end_id = args.end_point
    graph_file = args.graph_file

    # Load the airway graph. This must be an AirwayGraph type.
    graph = None
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)

    # Find the shortest path between the points.
    best_path = find_best_path(graph, start_id, end_id, verbose=True)

    # Print out a list of waypoints.
    wpt_plan = ""
    for wpt in best_path:
        wpt_plan += f"{wpt} "

    if len(best_path) > 0:
        print("RECOMMENDED FLIGHT PLAN:")
        print(wpt_plan)
    else:
        print("NO PATH FOUND.")
