using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    /// <summary>
    /// A destination item that pairs an MQTT navigation key with a localized display name.
    /// ToString() returns DisplayName so the default Picker rendering works without ItemDisplayBinding.
    /// </summary>
    public class DestinationItem
    {
        public string Key { get; }
        public string DisplayName { get; }
        public DestinationItem(string key, string displayName) { Key = key; DisplayName = displayName; }
        public override string ToString() => DisplayName;
    }

    public class DeliViewModel : BaseViewModel
    {
        private readonly IMqttService _mqtt;
        private readonly ISpeechService _speech;

        // Form fields
        private DestinationItem? _selectedDestinationItem;
        private string _item = string.Empty;
        private string _senderName = string.Empty;
        private string _receiverName = string.Empty;
        private string _note = string.Empty;

        // UI text
        private string _promptText = string.Empty;
        private string _titleText = string.Empty;
        private string _homeText = string.Empty;
        private string _languageLabel = "VI";
        private bool _isDelivering;
        private bool _isFormEnabled = true;

        // Static key-to-StringId mapping (language-independent keys)
        private static readonly List<(string Key, string StringId)> DestinationMap = new()
        {
            ("Water Intake",    StringIds.NAV_ROOM_WATER_INTAKE),
            ("Chemistry Hall",  StringIds.NAV_ROOM_CHEMISTRY_HALL),
            ("Restroom",        StringIds.NAV_ROOM_RESTROOM),
            ("Stairs",          StringIds.NAV_ROOM_STAIRS),
            ("Robotics Lab",    StringIds.NAV_ROOM_ROBOTICS_LAB),
            ("Electrical Lab",  StringIds.NAV_ROOM_ELECTRICAL_LAB),
            ("Home",  StringIds.NAV_ROOM_HOME),
        };

        private List<DestinationItem> _destinations = new();

        /// <summary>Localized destination list. Rebuilt automatically on language change.</summary>
        public List<DestinationItem> Destinations
        {
            get => _destinations;
            private set => SetProperty(ref _destinations, value);
        }

        public DestinationItem? SelectedDestinationItem
        {
            get => _selectedDestinationItem;
            set => SetProperty(ref _selectedDestinationItem, value);
        }
        public string Item
        {
            get => _item;
            set => SetProperty(ref _item, value);
        }
        public string SenderName
        {
            get => _senderName;
            set => SetProperty(ref _senderName, value);
        }
        public string ReceiverName
        {
            get => _receiverName;
            set => SetProperty(ref _receiverName, value);
        }
        public string Note
        {
            get => _note;
            set => SetProperty(ref _note, value);
        }
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
        public string LanguageLabel
        {
            get => _languageLabel;
            set => SetProperty(ref _languageLabel, value);
        }
        public bool IsDelivering
        {
            get => _isDelivering;
            set => SetProperty(ref _isDelivering, value);
        }
        public bool IsFormEnabled
        {
            get => _isFormEnabled;
            set => SetProperty(ref _isFormEnabled, value);
        }

        // Localized form labels
        public string FormTitle => StringIds.DELI_FORM_TITLE.GetString();
        public string DestinationLabel => StringIds.DELI_DESTINATION.GetString();
        public string ItemLabel => StringIds.DELI_ITEM_LABEL.GetString();
        public string SenderLabel => StringIds.DELI_SENDER_LABEL.GetString();
        public string ReceiverLabel => StringIds.DELI_RECEIVER_LABEL.GetString();
        public string NoteLabel => StringIds.DELI_NOTE_LABEL.GetString();
        public string StartDeliveryText => StringIds.DELI_START_DELIVERY.GetString();
        public string ReceivedText => StringIds.DELI_RECEIVED.GetString();
        public string ChooseDestinationText => StringIds.DELI_CHOOSE_DESTINATION.GetString();

        public Command StartDeliveryCommand { get; }
        public Command ReceivedCommand { get; }
        public Command GoHomeCommand { get; }
        public Command ToggleLanguageCommand { get; }

        public DeliViewModel(ILocalizationService localization, IMqttService mqtt, ISpeechService speech)
            : base(localization)
        {
            _mqtt = mqtt;
            _speech = speech;

            StartDeliveryCommand = new Command(OnStartDelivery, CanStartDelivery);
            ReceivedCommand = new Command(OnReceived);
            GoHomeCommand = new Command(async () =>
            {
                await _speech.StopSpeakingAsync();
                await Shell.Current.GoToAsync("//main");
            });
            ToggleLanguageCommand = new Command(() => Localization.ToggleLanguage());

            _mqtt.ArrivalReceived += OnArrivalReceived;
            RefreshLocalizedProperties();
        }

        protected override void RefreshLocalizedProperties()
        {
            TitleText = StringIds.DELI_TITLE.GetString();
            HomeText = StringIds.DELI_HOME.GetString();
            PromptText = IsDelivering
                ? StringIds.DELI_DELIVERING_NOW.GetString()
                : StringIds.DELI_GET_READY.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();

            // Rebuild the destinations list with translated names
            var previousKey = SelectedDestinationItem?.Key;
            var newList = DestinationMap
                .Select(d => new DestinationItem(d.Key, d.StringId.GetString()))
                .ToList();
            Destinations = newList;

            // Restore previous selection in new language
            SelectedDestinationItem = previousKey != null
                ? newList.FirstOrDefault(d => d.Key == previousKey)
                : null;

            OnPropertyChanged(nameof(FormTitle));
            OnPropertyChanged(nameof(DestinationLabel));
            OnPropertyChanged(nameof(ItemLabel));
            OnPropertyChanged(nameof(SenderLabel));
            OnPropertyChanged(nameof(ReceiverLabel));
            OnPropertyChanged(nameof(NoteLabel));
            OnPropertyChanged(nameof(StartDeliveryText));
            OnPropertyChanged(nameof(ReceivedText));
            OnPropertyChanged(nameof(ChooseDestinationText));
        }

        private bool CanStartDelivery() =>
            SelectedDestinationItem != null &&
            !string.IsNullOrWhiteSpace(Item) &&
            !string.IsNullOrWhiteSpace(SenderName) &&
            !string.IsNullOrWhiteSpace(ReceiverName);

        private async void OnStartDelivery()
        {
            if (!CanStartDelivery())
            {
                await Shell.Current.DisplayAlert(
                    TitleText,
                    "Please fill in all required fields.",
                    "OK");
                return;
            }

            IsDelivering = true;
            IsFormEnabled = false;
            PromptText = StringIds.DELI_DELIVERING_NOW.GetString();

            var msg = StringIds.DELI_DELIVERING_NOW.GetString();
            await _speech.SpeakAsync(msg, Localization.CurrentLanguageCode);

            if (!_mqtt.IsConnected)
                await _mqtt.ConnectAsync();

            // Publish the English navigation key (not the localized display name)
            await _mqtt.PublishGoalAsync(SelectedDestinationItem!.Key);
        }

        private void OnArrivalReceived(object? sender, bool arrived)
        {
            if (!arrived || !IsDelivering) return;
            PromptText = StringIds.DELI_ITEM_ARRIVED.GetString();
            _ = _speech.SpeakAsync(PromptText, Localization.CurrentLanguageCode);
        }

        private void OnReceived()
        {
            IsDelivering = false;
            IsFormEnabled = true;
            PromptText = StringIds.DELI_GET_READY.GetString();
            SelectedDestinationItem = null;
            Item = string.Empty;
            SenderName = string.Empty;
            ReceiverName = string.Empty;
            Note = string.Empty;
        }
    }
}
