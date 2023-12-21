
import argparse
import pandas as pd


def generate_airways_from_files(awy_file, fix_file, n_fix=5):
    """
    Generate an augmented airways database from official FAA data and GPS navaids.

    Arguments:
    - awy_file (str): File path for the FAA's NASR database AWY_SEG.csv
    - fix_file (str): File path for the FAA's NASR database FIX_BASE.csv
    - n_fix (int): Number of fixes at most to connect when generating augmented airways.
    """

    # Load the NASR airways
    nasr_airways_csv = pd.read_csv(awy_file)

    # Load the NASR fixes
    nasr_fix_base_csv = pd.read_csv(fix_file)
    
    # Return augmented airways
    # TODO: load in FIX_BASE.csv and create airways based on the N-closest fixes for a given fix.
    return nasr_airways_csv

if __name__ == "__main__":
    # Make this script configurable
    parser = argparse.ArgumentParser()
    parser.add_argument("--awy_file", required=False, default="data/AWY_SEG.csv")
    parser.add_argument("--fix_file", required=False, default="data/FIX_BASE.csv")

    # Parse the arguments
    args = parser.parse_args()
    awy_file = args.awy_file
    fix_file = args.fix_file

    awy_db = generate_airways_from_files(awy_file, fix_file)