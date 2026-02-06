import json
import os
import math

class RegulationsLoader:
    def __init__(self, json_path=None):
        if json_path is None:
            # Default to regulations.json in the same directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "regulations.json")
        
        self.json_path = json_path
        self.data = self._load_data()
        self.table_11 = self.data.get("table_11_flow_params", {}).get("data", [])
        self.table_12 = self.data.get("table_12_narrow_doors", {}).get("data", [])
        self.limits = self.data.get("limits", {})

    def _load_data(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading regulations.json: {e}")
            return {}

    def get_flow_params(self, density, path_type):
        """
        Retrieves v (speed) and q (specific throughput) from Table 11.
        Uses stricter 'Next Higher Value' interpolation for density.
        
        path_type: "horizontal", "stair_down", "stair_up", "door"
        """
        # Clamp density to max 9.2 (boundary condition)
        density = min(density, 9.2)
        
        # Mapping path_type to json keys
        type_map = {
            "horizontal": "horiz",
            "stair_down": "stair_down",
            "stair_up": "stair_up",
            "door": "door_wide"
        }
        
        key = type_map.get(path_type)
        if not key:
            raise ValueError(f"Unknown path_type: {path_type}")

        # Find the row with D >= density (Next Higher Value)
        selected_row = None
        for row in self.table_11:
            if row["D"] >= density:
                selected_row = row
                break
        
        # If density is higher than max in table, use the last row (should coincide with clamp)
        if selected_row is None:
            selected_row = self.table_11[-1]

        params = selected_row[key]
        return params["v"], params["q"]

    def get_narrow_door_params(self, width):
        """
        Retrieves q and v for narrow doors (0.6 <= width <= 1.6) at boundary density (9.2).
        Uses linear interpolation.
        """
        # Clamp width to table range
        width = max(0.6, min(width, 1.6))
        
        # Find bracketing rows
        lower = None
        upper = None
        
        for row in self.table_12:
            if row["width"] == width:
                return row["v"], row["q"]
            if row["width"] < width:
                lower = row
            if row["width"] > width and upper is None:
                upper = row
                break
        
        if lower and upper:
            # Interpolate
            ratio = (width - lower["width"]) / (upper["width"] - lower["width"])
            v = lower["v"] + (upper["v"] - lower["v"]) * ratio
            q = lower["q"] + (upper["q"] - lower["q"]) * ratio
            return v, q
            
        # Fallback (shouldn't happen with clamping)
        entry = lower if lower else upper
        return entry["v"], entry["q"]

    def get_limit(self, path_type, param):
        """
        Get q_max or q_gran for a path type.
        path_type: "horizontal", "stairs_down", "stairs_up", "doors"
        param: "q_max", "q_gran", "v_gran"
        """
        return self.limits.get(path_type, {}).get(param, 0.0)

    def get_permissible_time(self, category, sub_category=None):
        """
        Simple lookup for permissible time.
        In a real component, this might need expanded logic for all building types.
        """
        pt = self.data.get("permissible_time_limits", {})
        cat_data = pt.get(category)
        
        if isinstance(cat_data, dict):
            if sub_category:
                return cat_data.get(sub_category, 999.0) # 999 as 'unlimited' default logic placeholder
            else:
                 return cat_data
        elif isinstance(cat_data, (int, float)):
            return cat_data
            
        return 999.0
