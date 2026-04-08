using RobotHri.Languages;
using RobotHri.Services;
using System.Diagnostics;

namespace RobotHri
{
    public partial class App : Application
    {
        public App(ILocalizationService localization, IMqttService mqtt)
        {
            InitializeComponent();

            // Initialize localization (loads persisted language preference)
            var savedLang = Preferences.Get("app_language", "vi");
            localization.SetLanguage(savedLang);

            // Initialize Localize static layer for GetString() extension method
            Localize.SetLocalize(savedLang == "en" ? 2 : 1);

            // Warm up MQTT on app start instead of waiting for Navi page.
            _ = Task.Run(async () =>
            {
                try
                {
                    await mqtt.ConnectAsync();
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[MQTT] Startup connect failed: {ex.Message}");
                }
            });
        }

        protected override Window CreateWindow(IActivationState? activationState)
            => new Window(new AppShell());
    }
}
