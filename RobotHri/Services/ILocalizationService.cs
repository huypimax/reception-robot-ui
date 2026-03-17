namespace RobotHri.Services
{
    public interface ILocalizationService
    {
        string CurrentLanguageCode { get; }
        string GetString(string key);
        string Format(string key, params (string token, string value)[] args);
        void ToggleLanguage();
        void SetLanguage(string code);
        event EventHandler LanguageChanged;
        string GetCurrentLanguageName();
    }
}
