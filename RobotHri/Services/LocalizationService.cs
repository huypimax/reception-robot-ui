using RobotHri.Languages;

namespace RobotHri.Services
{
    /// <summary>
    /// Wraps Localize static class into an injectable service.
    /// Language persists via Preferences (replaces src/config.json).
    /// </summary>
    public class LocalizationService : ILocalizationService
    {
        private const string PreferenceKey = "app_language";

        public string CurrentLanguageCode =>
            Localize.CurrentLocaleCode.StartsWith("vi") ? "vi" : "en";

        public event EventHandler? LanguageChanged;

        public LocalizationService()
        {
            Localize.LanguageChanged += OnLocaleChanged;

            // Restore persisted language
            var saved = Preferences.Get(PreferenceKey, "vi");
            SetLanguage(saved);
        }

        public string GetString(string key) => key.GetString();

        public string Format(string key, params (string token, string value)[] args)
        {
            var template = key.GetString();
            return template.Format(args);
        }

        public void ToggleLanguage()
        {
            Localize.ToggleLanguage();
            Preferences.Set(PreferenceKey, CurrentLanguageCode);
        }

        public void SetLanguage(string code)
        {
            var locale = Localize.Locales.FirstOrDefault(l =>
                l.Code.StartsWith(code, StringComparison.OrdinalIgnoreCase));
            if (locale != null)
            {
                Localize.SetLocalize(locale.Id);
                Preferences.Set(PreferenceKey, code);
            }
        }

        public string GetCurrentLanguageName() =>
            CurrentLanguageCode.StartsWith("vi") ? "Tiếng Việt" : "English";

        private void OnLocaleChanged(object? sender, EventArgs e)
        {
            LanguageChanged?.Invoke(this, EventArgs.Empty);
        }
    }
}
