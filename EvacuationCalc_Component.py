"""
BG-Fire-Evac: Fire Safety Evacuation Calculator
Bulgarian Ordinance Iz-1971, Annex 8a

Inputs:
    Run (bool): Set to True to calculate
    Curves (list[Curve]): List of path curves (in order of travel)
    Room (Brep): The room/zone of origin (for area)
    N (int): Number of occupants
    BuildingCategory (str): e.g., "buildings_under_25m", "buildings_over_25m"
    SubCategory (str): e.g., "fire_resistance_I_II"

Outputs:
    TotalTime (float): Calculated Evacuation Time (min)
    PermissibleTime (float): Max allowed time (min)
    Compliance (str): "PASS" or "FAIL"
    Log (str): Calculation details
"""

import sys
import os

# Add the directory of this script to sys.path so we can import our modules
# In Grasshopper, __file__ might not point where we expect, or need to be handled carefuly.
# Ensuring the user saves this file in the evaccalc folder.
# For GhPython, we'll try to deduce path or assume standard lib path.

try:
    # Attempt to find the folder containing basic modules
    script_dir = os.path.dirname(os.path.abspath(__file__))
except:
    script_dir = "c:\\Users\\Dimitar\\evaccalc" # Fallback hardcode for this user env

if script_dir not in sys.path:
    sys.path.append(script_dir)

import regulations
import calculator
import geometry

# Reload for development (optional)
# reload(regulations)
# reload(calculator)
# reload(geometry)

def main():
    if not globals().get("Run", False):
        return

    # Check Inputs
    if not globals().get("Curves"): 
        print("Error: No Curves supplied")
        return
    if not globals().get("Room"): 
        print("Warning: No Room supplied, assuming 100m2")
    if not globals().get("N"):
        print("Error: N (occupants) not supplied")
        return

    occupants = int(N)
    
    # Process Room Area
    room_area = 100.0
    if Room:
        try:
             # Rhino.Geometry logic
            import Rhino.Geometry as rg
            amp = rg.AreaMassProperties.Compute(Room)
            if amp:
                room_area = amp.Area
        except:
            pass

    # Process Geometry
    geo_helper = geometry.GeometryHelper()
    segments = geo_helper.analyze_path(Curves)

    # Init Calculator
    reg_loader = regulations.RegulationsLoader()
    calc = calculator.EvacuationCalculator(reg_loader)

    # Run Calculation
    total_time, log_text = calc.calculate(segments, occupants, room_area)
    
    # Get Permissible Time
    cats = globals().get("BuildingCategory", "buildings_under_25m")
    sub_cats = globals().get("SubCategory", "fire_resistance_I_II")
    t_perm = reg_loader.get_permissible_time(cats, sub_cats)
    
    # Check Compliance
    compliance = "PASS"
    if isinstance(t_perm, (int, float)):
        if total_time > t_perm:
            compliance = "FAIL"
    else:
        t_perm = -1 # Unknown
        compliance = "UNKNOWN"

    # Set Outputs (Global variables in GhPython)
    global TotalTime, PermissibleTime, Compliance, Log
    TotalTime = total_time
    PermissibleTime = t_perm
    Compliance = compliance
    Log = log_text

if __name__ == "__main__":
    main()
