
import argparse
import pickle

from airway_graph import AirwayGraph


if __name__ == "__main__":
    # Make this script configurable
    parser = argparse.ArgumentParser()
    parser.add_argument("--awy_file", required=False, default="data/AWY_SEG.csv")
    parser.add_argument("--fix_file", required=False, default="data/FIX_BASE.csv")

    # Parse the arguments
    args = parser.parse_args()
    awy_file = args.awy_file
    fix_file = args.fix_file

    awy_graph = AirwayGraph()
    awy_graph.load_defined_airways(awy_file)
    awy_graph.build_custom_airways(fix_file)

    # Export the graph to a pickle file
    with open("data/airway_graph.pkl", "wb") as f:
        pickle.dump(awy_graph, f)