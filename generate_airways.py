
import argparse
import pickle

from airway_graph import AirwayGraph

if __name__ == "__main__":
    # Make this script configurable
    parser = argparse.ArgumentParser()
    parser.add_argument("--awy_file", required=False, default="data/AWY_SEG.csv")
    parser.add_argument("--fix_file", required=False, default="data/FIX_BASE.csv")
    parser.add_argument("--apt_file", required=False, default="data/APT_BASE.csv")
    parser.add_argument("--navaid_file", required=False, default="data/NAV_BASE.csv")
    parser.add_argument("--star_file", required=False, default="data/STAR_RTE.csv")
    parser.add_argument("--star_apt_file", required=False, default="data/STAR_APT.csv")
    parser.add_argument("--sid_file", required=False, default="data/DP_RTE.csv")
    parser.add_argument("--sid_apt_file", required=False, default="data/DP_APT.csv")
    parser.add_argument("--in_file", required=False, default="")
    parser.add_argument("--out_file", required=False, default="data/airway_graph.pkl")

    # Parse the arguments
    args = parser.parse_args()
    awy_file = args.awy_file
    fix_file = args.fix_file
    apt_file = args.apt_file
    navaid_file = args.navaid_file
    star_file = args.star_file
    star_apt_file = args.star_apt_file
    sid_file = args.sid_file
    sid_apt_file = args.sid_apt_file
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

    # Load data from all NASR subscription files.
    awy_graph.load_nasr_data(fix_file, apt_file, navaid_file, awy_file,
                             star_file, star_apt_file, sid_file, sid_apt_file)

    # Export the graph to a pickle file.
    with open(graph_out_file, "wb") as f:
        pickle.dump(awy_graph, f)

    print(f"Airway graph generated!")
