using RobotHri.Models;
using SQLite;

namespace RobotHri.Services
{
    public class SetupSettingsStore : ISetupSettingsStore
    {
        private readonly SQLiteAsyncConnection _connection;
        private bool _initialized;

        public SetupSettingsStore()
        {
            var dbPath = Path.Combine(FileSystem.AppDataDirectory, "robot_hri.db3");
            _connection = new SQLiteAsyncConnection(dbPath);
        }

        public async Task<SetupSettingsEntity> GetAsync()
        {
            await EnsureInitializedAsync();

            var settings = await _connection.Table<SetupSettingsEntity>()
                .Where(x => x.Id == 1)
                .FirstOrDefaultAsync();

            if (settings is not null)
                return settings;

            settings = new SetupSettingsEntity { Id = 1 };
            await _connection.InsertAsync(settings);
            return settings;
        }

        public async Task SaveAsync(SetupSettingsEntity settings)
        {
            await EnsureInitializedAsync();
            settings.Id = 1;
            await _connection.InsertOrReplaceAsync(settings);
        }

        private async Task EnsureInitializedAsync()
        {
            if (_initialized)
                return;

            await _connection.CreateTableAsync<SetupSettingsEntity>();
            _initialized = true;
        }
    }
}
