using System;
using System.Collections.Generic;
using System.Text;

namespace BG_Fire_Evac.Logic
{
    public class Segment
    {
        public double Length { get; set; }
        public double Width { get; set; } = 1.0;
        public string Type { get; set; } = "horizontal";
    }

    public class Calculator
    {
        private Regulations _reg;

        public Calculator()
        {
            _reg = new Regulations();
        }

        public double CalculateDensity(int N, double area)
        {
            if (area <= 0) return 9.2;
            double D = (double)N / area;
            return Math.Min(D, 9.2);
        }

        public (double totalTime, string log) Calculate(List<Segment> segments, int N, double startArea)
        {
            if (N <= 50)
            {
                return MethodL(segments, N, startArea);
            }
            else
            {
                return MethodQ(segments, N, startArea);
            }
        }

        private (double, string) MethodL(List<Segment> segments, int N, double startArea)
        {
            StringBuilder log = new StringBuilder();
            log.AppendLine("Method L Selected (N <= 50)");

            double totalTime = 0.0;
            double dStart = CalculateDensity(N, startArea);
            log.AppendLine($"Initial Density D = {dStart:F2} (N={N}, A={startArea:F2})");

            for (int i = 0; i < segments.Count; i++)
            {
                var seg = segments[i];
                var (v, q) = _reg.GetFlowParams(dStart, seg.Type);
                
                if (v <= 0) v = 0.1;

                double tSeg = seg.Length / v;
                totalTime += tSeg;
                log.AppendLine($"Seg {i + 1} ({seg.Type}): L={seg.Length:F2}m, v={v:F2}m/min -> t={tSeg:F2} min");
            }

            return (totalTime, log.ToString());
        }

        private (double, string) MethodQ(List<Segment> segments, int N, double startArea)
        {
            StringBuilder log = new StringBuilder();
            log.AppendLine("Method Q Selected (N > 50)");

            double dCurrent = CalculateDensity(N, startArea);
            log.AppendLine($"Initial Density D={dCurrent:F2}");

            double totalTime = 0.0;

            for (int i = 0; i < segments.Count; i++)
            {
                var seg = segments[i];
                var (vTable, qTable) = _reg.GetFlowParams(dCurrent, seg.Type);

                // Throughput time
                double throughput = seg.Width * qTable;
                if (throughput <= 0) throughput = 0.1;
                double tThroughput = N / throughput;

                // Travel time
                double tTravel = seg.Length / vTable;

                // Simplified conservative: max of flow time vs travel time
                double tSegment = Math.Max(tThroughput, tTravel);

                totalTime += tSegment;
                log.AppendLine($"Seg {i + 1}: W={seg.Width}m L={seg.Length}m Type={seg.Type} D={dCurrent:F2} -> q={qTable} v={vTable} -> T_calc={tSegment:F2}m");
            }

            return (totalTime, log.ToString());
        }
    }
}
