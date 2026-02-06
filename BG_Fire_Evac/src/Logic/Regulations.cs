using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;

namespace BG_Fire_Evac.Logic
{
    public class Regulations
    {
        private JsonDocument _data;
        private List<JsonElement> _table11;
        private List<JsonElement> _table12;
        private JsonElement _limits;
        private JsonElement _permissibleTimeLimits;

        public Regulations()
        {
            LoadData();
        }

        private void LoadData()
        {
            try
            {
                var assembly = Assembly.GetExecutingAssembly();
                using (var stream = assembly.GetManifestResourceStream("BG_Fire_Evac.src.Resources.regulations.json"))
                using (var reader = new StreamReader(stream))
                {
                    string json = reader.ReadToEnd();
                    _data = JsonDocument.Parse(json);
                    
                    var root = _data.RootElement;
                    _table11 = root.GetProperty("table_11_flow_params").GetProperty("data").EnumerateArray().ToList();
                    _table12 = root.GetProperty("table_12_narrow_doors").GetProperty("data").EnumerateArray().ToList();
                    _limits = root.GetProperty("limits");
                    _permissibleTimeLimits = root.GetProperty("permissible_time_limits");
                }
            }
            catch (Exception ex)
            {
                // In Grasshopper, we might want to throw or log this
                throw new InvalidOperationException("Failed to load embedded regulations.json", ex);
            }
        }

        public (double v, double q) GetFlowParams(double density, string pathType)
        {
            // Clamp density to max 9.2
            density = Math.Min(density, 9.2);

            string key = pathType switch
            {
                "horizontal" => "horiz",
                "stair_down" => "stair_down",
                "stair_up" => "stair_up",
                "door" => "door_wide",
                _ => throw new ArgumentException($"Unknown path_type: {pathType}")
            };

            JsonElement? selectedRow = null;

            // Next Higher Value interpolation
            foreach (var row in _table11)
            {
                if (row.GetProperty("D").GetDouble() >= density)
                {
                    selectedRow = row;
                    break;
                }
            }

            if (selectedRow == null)
            {
                selectedRow = _table11.Last();
            }

            var paramsObj = selectedRow.Value.GetProperty(key);
            return (paramsObj.GetProperty("v").GetDouble(), paramsObj.GetProperty("q").GetDouble());
        }

        public double GetPermissibleTime(string category, string subCategory = null)
        {
            if (_permissibleTimeLimits.TryGetProperty(category, out JsonElement catData))
            {
                if (catData.ValueKind == JsonValueKind.Object && subCategory != null)
                {
                    if (catData.TryGetProperty(subCategory, out JsonElement subVal))
                    {
                        return subVal.GetDouble();
                    }
                }
                else if (catData.ValueKind == JsonValueKind.Number)
                {
                    return catData.GetDouble();
                }
            }
            return 999.0; // Default unlimited
        }
    }
}
