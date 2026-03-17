using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri
{
    public partial class App : Application
    {
        public App(ILocalizationService localization)
        {
            InitializeComponent();

            // Initialize localization (loads persisted language preference)
            var savedLang = Preferences.Get("app_language", "vi");
            localization.SetLanguage(savedLang);

            // Initialize Localize static layer for GetString() extension method
            Localize.SetLocalize(savedLang == "en" ? 2 : 1);
        }

        protected override Window CreateWindow(IActivationState? activationState)
            => new Window(new AppShell());
    }
}
