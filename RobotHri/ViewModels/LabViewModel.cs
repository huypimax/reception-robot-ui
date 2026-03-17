using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    public class LabViewModel : BaseViewModel
    {
        private readonly ISpeechService _speech;

        private string _promptText = string.Empty;
        private string _titleText = string.Empty;
        private string _homeText = string.Empty;
        private string _backText = string.Empty;
        private string _languageLabel = "VI";
        private string _readAloudText = string.Empty;
        private string? _selectedDevice;
        private string _deviceTitle = string.Empty;
        private string _deviceDescription = string.Empty;
        private string _deviceImageSource = string.Empty;
        private bool _isDetailVisible;

        public string PromptText
        {
            get => _promptText;
            set => SetProperty(ref _promptText, value);
        }
        public string TitleText
        {
            get => _titleText;
            set => SetProperty(ref _titleText, value);
        }
        public string HomeText
        {
            get => _homeText;
            set => SetProperty(ref _homeText, value);
        }
        public string BackText
        {
            get => _backText;
            set => SetProperty(ref _backText, value);
        }
        public string LanguageLabel
        {
            get => _languageLabel;
            set => SetProperty(ref _languageLabel, value);
        }
        public string ReadAloudText
        {
            get => _readAloudText;
            set => SetProperty(ref _readAloudText, value);
        }
        public string? SelectedDevice
        {
            get => _selectedDevice;
            set => SetProperty(ref _selectedDevice, value);
        }
        public string DeviceTitle
        {
            get => _deviceTitle;
            set => SetProperty(ref _deviceTitle, value);
        }
        public string DeviceDescription
        {
            get => _deviceDescription;
            set => SetProperty(ref _deviceDescription, value);
        }
        /// <summary>Image file name for the selected device (shown in detail view)</summary>
        public string DeviceImageSource
        {
            get => _deviceImageSource;
            set => SetProperty(ref _deviceImageSource, value);
        }
        public bool IsDetailVisible
        {
            get => _isDetailVisible;
            set 
            {
                SetProperty(ref _isDetailVisible, value);
                HomeText = value ? StringIds.LAB_BACK.GetString() : StringIds.LAB_HOME.GetString();
            }
        }

        // Device button labels (localized)
        public string DeviceIfmLabel => StringIds.LAB_ABOUT_IFM.GetString();
        public string DevicePlcLabel => StringIds.LAB_ABOUT_PLC.GetString();
        public string DeviceStepLabel => StringIds.LAB_ABOUT_STEP.GetString();
        public string DeviceHmiLabel => StringIds.LAB_ABOUT_HMI.GetString();

        public Command<string> SelectDeviceCommand { get; }
        public Command ReadAloudCommand { get; }
        public Command BackCommand { get; }
        public Command GoHomeCommand { get; }
        public Command ToggleLanguageCommand { get; }

        public LabViewModel(ILocalizationService localization, ISpeechService speech) : base(localization)
        {
            _speech = speech;
            SelectDeviceCommand = new Command<string>(OnDeviceSelected);
            ReadAloudCommand = new Command(OnReadAloud);
            BackCommand = new Command(OnBack);
            GoHomeCommand = new Command(async () =>
            {
                await _speech.StopSpeakingAsync();
                await Shell.Current.GoToAsync("//main");
            });
            ToggleLanguageCommand = new Command(() => Localization.ToggleLanguage());
            RefreshLocalizedProperties();
        }

        protected override void RefreshLocalizedProperties()
        {
            TitleText = StringIds.LAB_TITLE.GetString();
            PromptText = StringIds.LAB_PROMPT.GetString();
            HomeText = IsDetailVisible ? StringIds.LAB_BACK.GetString() : StringIds.LAB_HOME.GetString();
            BackText = StringIds.LAB_BACK.GetString();
            ReadAloudText = StringIds.LAB_READ_ALOUD.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();

            OnPropertyChanged(nameof(DeviceIfmLabel));
            OnPropertyChanged(nameof(DevicePlcLabel));
            OnPropertyChanged(nameof(DeviceStepLabel));
            OnPropertyChanged(nameof(DeviceHmiLabel));

            // Refresh detail text if already showing
            if (!string.IsNullOrEmpty(SelectedDevice))
                LoadDeviceDetail(SelectedDevice);
        }

        private void OnDeviceSelected(string deviceKey)
        {
            SelectedDevice = deviceKey;
            LoadDeviceDetail(deviceKey);
            IsDetailVisible = true;
        }

        private void LoadDeviceDetail(string deviceKey)
        {
            (DeviceTitle, DeviceDescription, DeviceImageSource) = deviceKey switch
            {
                "ifm" => (StringIds.LAB_ABOUT_IFM.GetString(),
                          StringIds.LAB_DEVICE_IFM.GetString(),
                          "lab_ifm.png"),
                "plc" => (StringIds.LAB_ABOUT_PLC.GetString(),
                          StringIds.LAB_DEVICE_PLC.GetString(),
                          "lab_plc.png"),
                "step" => (StringIds.LAB_ABOUT_STEP.GetString(),
                           StringIds.LAB_DEVICE_STEP.GetString(),
                           "lab_step.png"),
                "hmi" => (StringIds.LAB_ABOUT_HMI.GetString(),
                          StringIds.LAB_DEVICE_HMI.GetString(),
                          "lab_hmi.png"),
                _ => (string.Empty, string.Empty, string.Empty)
            };
        }

        private async void OnReadAloud()
        {
            if (!string.IsNullOrEmpty(DeviceDescription))
                await _speech.SpeakAsync(DeviceDescription, Localization.CurrentLanguageCode);
        }

        private async void OnBack()
        {
            await _speech.StopSpeakingAsync();
            IsDetailVisible = false;
            SelectedDevice = null;
            DeviceTitle = string.Empty;
            DeviceDescription = string.Empty;
            DeviceImageSource = string.Empty;
        }

        public async Task StopSpeechAsync() => await _speech.StopSpeakingAsync();
    }
}
