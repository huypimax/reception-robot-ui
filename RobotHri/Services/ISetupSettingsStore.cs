using RobotHri.Models;

namespace RobotHri.Services
{
    public interface ISetupSettingsStore
    {
        Task<SetupSettingsEntity> GetAsync();
        Task SaveAsync(SetupSettingsEntity settings);
    }
}
