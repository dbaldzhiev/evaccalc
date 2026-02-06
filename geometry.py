import math

# Since this runs in Grasshopper, we would typically import Rhino.Geometry
# But for unit testing outside Rhino, we need to mock or inspect imports.
try:
    import Rhino.Geometry as rg
except ImportError:
    rg = None

class GeometryHelper:
    def __init__(self):
        pass

    def get_seg_type(self, curve):
        """
        Identifies if a curve is horizontal, stair up/down, or door.
        In detailed GH implementation, this might read User Data or Layer names.
        For now, simplistic logic based on slope.
        """
        if not rg:
            return "horizontal" # Default for non-Rhino env

        start = curve.PointAtStart
        end = curve.PointAtEnd
        length_3d = curve.GetLength()
        
        dz = end.Z - start.Z
        length_plan = math.sqrt(length_3d**2 - dz**2) if length_3d > abs(dz) else 0.001
        
        slope_deg = math.degrees(math.atan2(abs(dz), length_plan))
        
        if slope_deg < 5:
            return "horizontal"
        else:
            if dz < 0:
                return "stair_down"
            else:
                return "stair_up"
                
    def analyze_path(self, curves):
        """
        Converts a list of Rhino Curves into segment dictionaries.
        """
        segments = []
        if not curves:
            return segments
            
        for crv in curves:
            if crv is None: continue
            
            # length = crv.GetLength() if rg else 10.0
            
            # Mocking for pure python testability if rg is missing
            if rg:
                length = crv.GetLength()
                seg_type = self.get_seg_type(crv)
            else:
                length = 10.0 # Placeholder
                seg_type = "horizontal"
            
            # Width would need to be passed separately or attached as data
            width = 1.0 # Default
            
            segments.append({
                "length": length,
                "type": seg_type,
                "width": width
            })
            
        return segments
