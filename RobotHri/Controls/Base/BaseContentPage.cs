using RobotHri.Services;

namespace RobotHri.Controls.Base
{
    /// <summary>
    /// Base page for all Robot HRI pages.
    /// Mirrors CloudBanking's BaseDialog — handles language change notifications
    /// and provides common service access.
    /// </summary>
    public abstract class BaseContentPage : ContentPage
    {
        protected ILocalizationService Localization { get; }

        protected BaseContentPage()
        {
            Localization = ServiceHelper.GetService<ILocalizationService>()!;
            Localization.LanguageChanged += OnLanguageChanged;
        }

        /// <summary>
        /// Called when the active language changes. Override to update UI strings.
        /// </summary>
        protected virtual void OnLanguageChanged(object? sender, EventArgs e)
        {
            MainThread.BeginInvokeOnMainThread(RefreshLocalizedText);
        }

        /// <summary>
        /// Override to refresh all localized text in the page.
        /// </summary>
        protected virtual void RefreshLocalizedText() { }

        protected override void OnDisappearing()
        {
            base.OnDisappearing();
            Localization.LanguageChanged -= OnLanguageChanged;
        }

        protected override void OnAppearing()
        {
            base.OnAppearing();
            Localization.LanguageChanged += OnLanguageChanged;
            RefreshLocalizedText();
        }
    }

    /// <summary>
    /// Static helper to resolve services from the DI container.
    /// </summary>
    public static class ServiceHelper
    {
        public static TService? GetService<TService>() where TService : class
            => IPlatformApplication.Current?.Services.GetService<TService>();
    }
}
