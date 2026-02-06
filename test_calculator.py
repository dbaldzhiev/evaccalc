import unittest
import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculator import EvacuationCalculator
from regulations import RegulationsLoader

class TestEvacuationCalculator(unittest.TestCase):
    def setUp(self):
        self.reg = RegulationsLoader() # Load real json
        self.calc = EvacuationCalculator(self.reg)

    def test_density_calculation(self):
        # D = N/A
        d = self.calc.calculate_density(10, 100) # 0.1
        self.assertAlmostEqual(d, 0.1)
        
        # Clamp check
        d_high = self.calc.calculate_density(1000, 10) # 100 -> 9.2
        self.assertEqual(d_high, 9.2)

    def test_method_selection(self):
        self.assertEqual(self.calc.select_method(50), "Method L")
        self.assertEqual(self.calc.select_method(51), "Method Q")

    def test_method_L_simple(self):
        # N=10, Area=100 -> D=0.1
        # Table 11: D=0.1 -> v_horiz = 100
        # Segment 10m
        segments = [{"length": 10.0, "type": "horizontal"}]
        time, log = self.calc.method_L(segments, 10, 100.0)
        
        # T = 10 / 100 = 0.1 min
        self.assertAlmostEqual(time, 0.1)

    def test_method_Q_simple(self):
        # N=60, Area=100 -> D=0.6 -> interpolate to D=1.0 logic?
        # Regulations logic in reg.py: next higher value.
        # D=0.6 -> Next is D=1.0.
        # Table 11 D=1.0 Horiz: v=80.14, q=80.1
        
        # Segment: 10m long, width 1.0m
        segments = [{"length": 10.0, "width": 1.0, "type": "horizontal"}]
        
        # Method Q logic in calc.py uses max(t_throughput, t_travel) per segment (simplified)
        
        # t_throughput = N / (W*q) = 60 / (1.0 * 80.1) = 0.749 min
        # t_travel = L / v = 10 / 80.14 = 0.124 min
        # Max = 0.749
        
        time, log = self.calc.method_Q(segments, 60, 100.0)
        
        expected_q = 80.1
        expected_t = 60 / expected_q
        self.assertAlmostEqual(time, expected_t, places=2)

if __name__ == '__main__':
    unittest.main()
