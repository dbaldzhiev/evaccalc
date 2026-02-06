# Project: BG-Fire-Evac (Rhino/Grasshopper Plugin)

## Overview
[cite_start]We are building a computational design tool to automate fire safety compliance checks according to Bulgarian Ordinance Iz-1971, specifically **Annex 8a (Приложение № 8а)**[cite: 1]. The tool will calculate evacuation times based on building geometry and occupant density, comparing the results against permissible legal limits.

## Core Objective
Calculate the Total Evacuation Time ($\tau_{EB}$) using two legally defined methods and validate if $\tau_{EB} \le t_{perm}$ (Permissible Time).

## Technology Stack
- **Host:** Rhino 8 / Grasshopper
- **Language:** C# .NET Grasshopper Plugin (compiled .gha)
- **Data Format:** JSON for regulatory tables (Embedded resource or external file)
- **Input:** Rhino Curves (Path), Breps (Rooms), and User Parameters.