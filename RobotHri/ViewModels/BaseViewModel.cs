using System.ComponentModel;
using System.Runtime.CompilerServices;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    /// <summary>
    /// Base ViewModel with INotifyPropertyChanged and localization support.
    /// </summary>
    public abstract class BaseViewModel : INotifyPropertyChanged
    {
        protected readonly ILocalizationService Localization;

        private bool _isBusy;
        private string _title = string.Empty;

        public bool IsBusy
        {
            get => _isBusy;
            set => SetProperty(ref _isBusy, value);
        }

        public string Title
        {
            get => _title;
            set => SetProperty(ref _title, value);
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected BaseViewModel(ILocalizationService localization)
        {
            Localization = localization;
            Localization.LanguageChanged += OnLanguageChanged;
        }

        /// <summary>
        /// Called when language changes — override to refresh localized properties.
        /// </summary>
        protected virtual void OnLanguageChanged(object? sender, EventArgs e)
        {
            RefreshLocalizedProperties();
        }

        /// <summary>
        /// Override to notify property changes for all localized string properties.
        /// </summary>
        protected virtual void RefreshLocalizedProperties() { }

        protected bool SetProperty<T>(ref T backingStore, T value,
            [CallerMemberName] string propertyName = "",
            Action? onChanged = null)
        {
            if (EqualityComparer<T>.Default.Equals(backingStore, value))
                return false;

            backingStore = value;
            onChanged?.Invoke();
            OnPropertyChanged(propertyName);
            return true;
        }

        protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
