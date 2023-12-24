
import argparse
import pickle

from airway_graph import AirwayGraph

if __name__ == "__main__":
    # Make this script configurable
    parser = argparse.ArgumentParser()
    parser.add_argument("--awy_file", required=False, default="data/AWY_SEG.csv")
    parser.add_argument("--fix_file", required=False, default="data/FIX_BASE.csv")
    parser.add_argument("--navaid_file", required=False, default="data/NAV_BASE.csv")
    parser.add_argument("--in_file", required=False, default="")
    parser.add_argument("--out_file", required=False, default="data/airway_graph.pkl")

    # Parse the arguments
    args = parser.parse_args()
    awy_file = args.awy_file
    fix_file = args.fix_file
    navaid_file = args.navaid_file
    graph_in_file = args.in_file
    graph_out_file = args.out_file

    # If there is a graph input file, load the saved graph.
    awy_graph = None
    if graph_in_file != "":
        with open(graph_in_file, 'rb') as f:
            awy_graph = pickle.load(f)
    else:
        # Otherwise create a new airway graph.
        awy_graph = AirwayGraph()

    # Load the NASR fixes into the graph.
    awy_graph.load_nasr_fixes(fix_file)

    # Load the NASR navaids into the graph.
    awy_graph.load_nasr_navaids(navaid_file)

    # Update the graph based on the NASR database information.
    awy_graph.load_nasr_airways(awy_file)

    # TODO: Load standard departures

    # TODO: Load standard arrivals

    # Export the graph to a pickle file.
    with open(graph_out_file, "wb") as f:
        pickle.dump(awy_graph, f)

    print(f"Airway graph generated!")
