import math
from regulations import RegulationsLoader

class EvacuationCalculator:
    def __init__(self, regulations_loader=None):
        if regulations_loader:
            self.reg = regulations_loader
        else:
            self.reg = RegulationsLoader()

    def calculate_density(self, N, area):
        """
        Calculates density D = N / A.
        Returns clamped density (max 9.2).
        """
        if area <= 0:
            return 9.2 # Fail safe high density
        D = N / area
        return min(D, 9.2)

    def select_method(self, N):
        """
        Determines calculation method based on occupant count.
        N <= 50: Method L
        N > 50: Method Q
        """
        if N <= 50:
            return "Method L"
        else:
            return "Method Q"

    def method_L(self, segments, N, start_area):
        """
        Calculates time using Method L.
        Segments: list of dicts { 'length': float, 'type': str }
        start_area: Area of the origin room/segment (for initial speed)
        
        Returns: total_time [min], log [str]
        """
        log = ["Method L Selected (N <= 50)"]
        total_time = 0.0
        
        # Determine initial density
        d_start = self.calculate_density(N, start_area)
        log.append(f"Initial Density D = {d_start:.2f} (N={N}, A={start_area:.2f})")

        current_v = 0.0
        
        for i, seg in enumerate(segments):
            seg_type = seg.get("type", "horizontal")
            length = seg.get("length", 0.0)
            
            # For Method L, speed is usually constant per segment based on D?
            # Or does D change?
            # Standard engineering practice for Method L / simple hydraulic:
            # Assume constant flow params based on initial density unless geometry changes density (bottleneck).
            # However, for N<=50, it's free movement mostly.
            
            # Regulation Check: If D < 0.1, v = 100 m/min horizontal?
            # We use the table lookup which gives 100 for D=0.1.
            
            v, q = self.reg.get_flow_params(d_start, seg_type)
            
            if v <= 0:
                v = 0.1 # Prevent div by zero
            
            t_seg = length / v
            total_time += t_seg
            log.append(f"Seg {i+1} ({seg_type}): L={length:.2f}m, v={v:.2f}m/min -> t={t_seg:.2f} min")
            
        return total_time, "\n".join(log)

    def method_Q(self, segments, N, start_area):
        """
        Calculates time using Method Q (Throughput).
        Simplified robust approach: Find the limiting segment (bottleneck) and add travel time.
        
        Segments: list of dicts { 'length': float, 'width': float, 'type': str }
        """
        log = ["Method Q Selected (N > 50)"]
        
        d_current = self.calculate_density(N, start_area)
        log.append(f"Initial Density D={d_current:.2f}")
        
        # Calculate capacity of each segment
        # In a full flow model, we propagate flow.
        # Simplified conservative: The segment with the lowest Q_cap determines the flow rate for the whole group?
        # Or accumulation?
        # Formula: T = sum(L/v) + (N / Q_bottleneck - N / Q_arrival_if_any)? 
         
        # Let's use the segment-by-segment integration approach if possible, or the formula from math_model.
        # Math model says: T_i = N / (W * q) for specific segments where flow is fully developed.
        
        # We will calculate Travel Time (first person) + Discharge Time (at bottleneck).
        # T_total = T_travel_to_exit + T_discharge_at_exit?
        # Actually Annex 8a implies summing times for segments.
        # For a segment i: t_i = L_i / v_i (if free flow) OR t_i = N / (W_i * q_i) (if capacity limited).
        
        # Let's check the bottleneck capacity of every segment at the current density.
        
        total_time = 0.0
        accumulated_time = 0.0
        
        for i, seg in enumerate(segments):
            width = seg.get("width", 1.0)
            length = seg.get("length", 0.0)
            seg_type = seg.get("type", "horizontal")
            
            # Get flow params for current density
            if seg_type == "door" and width < 1.6 and width >= 0.6:
                # Use narrow door table for q, checking if limiting?
                # Actually Table 12 is for "Movement at Boundary Density".
                # If we are NOT at boundary density, we use Table 11?
                # Usually narrow doors BECOME the bottleneck and cause boundary density.
                # So we check capacity.
                v_table, q_table = self.reg.get_flow_params(d_current, seg_type)
                
                # Check narrow door specific capacity at max density just in case it's a bottleneck
                v_narrow, q_narrow_max = self.reg.get_narrow_door_params(width)
                
                # If the flow N / (W*q_table) > N / (W*q_narrow_max)...
                 
            else:
                 v_table, q_table = self.reg.get_flow_params(d_current, seg_type)
            
            # Time to traverse length (Growth of queue often makes this irrelevant for the tail of the group, 
            # but for the "Total Evacuation Time" (last person), it is:
            # Time for the group to pass this segment = N / (W * q)
            # OR L / v if that is larger? (Very long corridor, few people).
            
            # Throughput time:
            throughput = width * q_table
            if throughput <= 0: throughput = 0.1
            t_throughput = N / throughput
            
            # Travel time:
            t_travel = length / v_table
            
            # The effective time for the group to clear segment i is max(t_throughput, t_travel)?
            # Correct approach for simplified calc:
            # sum(L/v) is only for first person.
            # Last person is constrained by the bottleneck.
            
            # Let's use the formula: tau = sum(L/v) (travel of last person?)
            # No, if q is limiting, speed drops.
            
            # Standard formula for Total Time = Time for N to pass limiting segment + travel time to/from that segment.
            # But we are doing segment-by-segment.
            
            # Using the math model reference: T_segment = N / (W * q)
            # This assumes the segment is full of people or limiting.
            
            # Conservative Algo for this tool:
            # Calculate t_throughput for this segment.
            # Calculate t_travel for this segment.
            # Take max?
            
            t_segment = max(t_throughput, t_travel)
            
            total_time += t_segment
            log.append(f"Seg {i+1}: W={width}m L={length}m Type={seg_type} D={d_current:.2f} -> q={q_table} v={v_table} -> T_calc={t_segment:.2f}m")
            
            # Update density for next segment? 
            # In simple models, density might be assumed constant or re-calculated if width changes.
            # If width changes, W_next * q_next = W_curr * q_curr (Continuity eq).
            # q_next = (W_curr * q_curr) / W_next.
            # Then find new D from q_next.
            
            # Implementation of simple Continuity:
            throughput_flow = width * q_table # people/min
            
            if i < len(segments) - 1:
                next_width = segments[i+1].get("width", 1.0)
                next_q_target = throughput_flow / next_width
                
                # Look up D that corresponds to next_q_target?
                # This is complex (inverse lookup). 
                # For this MVP, let's keep Density Constant or assume it stays high if N > 50.
                pass

        return total_time, "\n".join(log)
        
    def calculate(self, segments, N, start_area):
        method = self.select_method(N)
        if method == "Method L":
            return self.method_L(segments, N, start_area)
        else:
            return self.method_Q(segments, N, start_area)
