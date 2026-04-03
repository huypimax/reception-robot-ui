using System.Text.Json.Serialization;

namespace RobotHri.Models
{
    public class LocationModel
    {
        [JsonPropertyName("x")]
        public double X { get; set; }

        [JsonPropertyName("y")]
        public double Y { get; set; }

        [JsonPropertyName("theta")]
        public double Theta { get; set; }
    }
}
