using RobotHri.Models;

namespace RobotHri.Services
{
    public interface IMqttService
    {
        bool IsConnected { get; }

        Task<bool> ConnectAsync();
        Task DisconnectAsync();
        Task PublishGoalAsync(string destination);
        Task PublishWaypointsAsync(IEnumerable<LocationModel> waypoints);
        Task PublishSpeedSettingsAsync(double normalSpeed, double rotationSpeed, double roughTerrainSpeed);

        event EventHandler<bool> ArrivalReceived;
        event EventHandler<LocationModel> LocationUpdated;
    }
}
