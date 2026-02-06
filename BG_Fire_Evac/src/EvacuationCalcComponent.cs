using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Rhino.Geometry;
using BG_Fire_Evac.Logic;

namespace BG_Fire_Evac
{
    public class EvacuationCalcComponent : GH_Component
    {
        private Calculator _calculator;

        public EvacuationCalcComponent()
          : base("Evacuation Calculator", "EvacCalc",
              "Calculates Total Evacuation Time according to Bulgarian Ordinance Iz-1971 (Annex 8a)",
              "BG-Fire-Evac", "Auditing")
        {
            _calculator = new Calculator();
        }

        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddBooleanParameter("Run", "Run", "Run the calculation", GH_ParamAccess.item, false);
            pManager.AddCurveParameter("Curves", "Crvs", "Evacuation path curves", GH_ParamAccess.list);
            pManager.AddBrepParameter("Room", "Room", "Room geometry (for area calculation)", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Occupants", "N", "Number of occupants", GH_ParamAccess.item, 0);
            pManager.AddTextParameter("BuildingCategory", "Cat", "Building Category (e.g. 'buildings_under_25m')", GH_ParamAccess.item, "buildings_under_25m");
            pManager.AddTextParameter("SubCategory", "SubCat", "Sub Category (e.g. 'fire_resistance_I_II')", GH_ParamAccess.item, "");
            
            pManager[5].Optional = true;
        }

        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddNumberParameter("TotalTime", "T_evac", "Total Evacuation Time (min)", GH_ParamAccess.item);
            pManager.AddNumberParameter("PermissibleTime", "T_perm", "Permissible Evacuation Time (min)", GH_ParamAccess.item);
            pManager.AddTextParameter("Compliance", "OK?", "Compliance Status", GH_ParamAccess.item);
            pManager.AddTextParameter("Log", "Log", "Calculation Log", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            bool run = false;
            if (!DA.GetData(0, ref run)) return;
            if (!run) return;

            List<Curve> curves = new List<Curve>();
            if (!DA.GetDataList(1, curves)) return;

            Brep room = null;
            if (!DA.GetData(2, ref room)) return;

            int n = 0;
            if (!DA.GetData(3, ref n)) return;

            string category = "";
            if (!DA.GetData(4, ref category)) return;

            string subCategory = "";
            DA.GetData(5, ref subCategory);

            // 1. Analyze Geometry
            var segments = new List<Segment>();
            foreach (var crv in curves)
            {
                if (crv == null) continue;
                
                segments.Add(new Segment
                {
                    Length = crv.GetLength(),
                    Type = GetSegmentType(crv),
                    Width = 1.0 // TODO: Get width from attributes or input? defaulting to 1.0m
                });
            }

            // 2. Calculate Area
            double area = room.GetArea();

            // 3. Run Calculation
            var (totalTime, log) = _calculator.Calculate(segments, n, area);

            // 4. Check Compliance
            // Need a way to access regulations loader from here or calculator
            // Simplest is to expose it or instantiate Regulations locally just for this check
            // For MVP, instantiation is fine (it's fast)
            var reg = new Regulations();
            double permTime = reg.GetPermissibleTime(category, subCategory);

            string compliance = (totalTime <= permTime) ? "PASS" : "FAIL";

            // 5. Set Outputs
            DA.SetData(0, totalTime);
            DA.SetData(1, permTime);
            DA.SetData(2, compliance);
            DA.SetData(3, log);
        }

        private string GetSegmentType(Curve curve)
        {
            Point3d start = curve.PointAtStart;
            Point3d end = curve.PointAtEnd;
            double length3d = curve.GetLength();
            double dz = end.Z - start.Z;
            
            double lengthPlan = Math.Sqrt(Math.Max(0, length3d * length3d - dz * dz));
            if (lengthPlan < 0.001) lengthPlan = 0.001;

            double slopeDeg = Math.Atan2(Math.Abs(dz), lengthPlan) * (180 / Math.PI);

            if (slopeDeg < 5) return "horizontal";
            if (dz < 0) return "stair_down";
            return "stair_up";
        }

        protected override System.Drawing.Bitmap Icon => null; // TODO: Add icon
        
        public override Guid ComponentGuid => new Guid("910243aa-4ef7-4620-b5e9-8816ab715d78"); // Unique ID
    }
}
