namespace RobotHri.Models
{
    /// <summary>
    /// Represents a single scheduled task shown in the Time-settings table.
    /// </summary>
    public class TimeTask
    {
        public int    Index    { get; set; }
        public string Time     { get; set; } = string.Empty;
        public string TaskName { get; set; } = string.Empty;
        public string TaskType { get; set; } = string.Empty;
        public string Number   { get; set; } = string.Empty;
        public string Route    { get; set; } = string.Empty;
        public string Repeat   { get; set; } = string.Empty;
    }
}
