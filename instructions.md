# BG-Fire-Evac Plugin Instructions

## Overview
This plugin calculates the Total Evacuation Time ($\tau_{EB}$) according to Bulgarian Ordinance Iz-1971 (Annex 8a). It automatically selects **Method L** (Length) or **Method Q** (Throughput) based on the occupant load.

## Setup regarding Development
1. **Prerequisites**:
   - Visual Studio 2022 (or later) with .NET Desktop Development workload.
   - Rhino 8 installed.
   - Grasshopper (built-in to Rhino).

2. **Building the Solution**:
   - Open the solution file (`.sln`) in Visual Studio.
   - Restore NuGet packages (including `RhinoCommon` and `Grasshopper`).
   - Build the solution in **Release** mode.
   - The output file `BG_Fire_Evac.gha` (and potentially `BG_Fire_Evac.dll`) will be generated in `bin\Release`.

## Installation for Users
1. Launch Rhino and run command `Grasshopper`.
2. Drag and drop the generated `BG_Fire_Evac.gha` file into the Grasshopper canvas.
   - Alternatively, place the `.gha` file in the special components folder: `%APPDATA%\Grasshopper\Libraries`.
3. Restart Rhino if necessary.

## Usage in Grasshopper
1. Look for the **BG-Fire-Evac** category in the Grasshopper toolbar.
2. Place the **Evacuation Calculator** component.
3. Provide the following **Inputs**:
   - `Run` (Boolean) - Set to True to execute.
   - `Curves` (List of Curve) - Evacuation paths.
   - `Room` (Brep) - The room or zone geometry (for area calculation).
   - `N` (Integer) - Number of occupants.
   - `BuildingCategory` (String) - e.g., "buildings_under_25m".
   - `SubCategory` (String) - e.g., "fire_resistance_I_II".
4. Read the **Outputs**:
   - `TotalTime` (Number) - Calculated $\tau_{EB}$.
   - `PermissibleTime` (Number) - Limit $t_{perm}$ from regulations.
   - `Compliance` (Boolean/Text) - Result of the check.
   - `Log` (Text) - Detailed calculation steps or error messages.

## Data Reference
- **Method L**: Used when $N \le 50$. Sums travel time based on speed from density.
- **Method Q**: Used when $N > 50$. Calculates throughput time at bottlenecks.
- **Density**: Calculated as $N / Area$. Clamped at 9.2 people/m².
- **Speed/Throughput**: Looked up from internal regulation tables (derived from Ordinance Iz-1971).

## Troubleshooting
- **Component Red/Error**: Right-click the component and check "Runtime Warnings" for error details.
- **"IndexOutOfRangeException"**: Check if your `BuildingCategory` or `SubCategory` strings match the allowed keys in the regulations.
- **Plugin not appearing**: Ensure the `.gha` file is unblocked (Right-click file -> Properties -> Unblock) and located in a trusted folder.
