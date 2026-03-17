using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    public class NaviViewModel : BaseViewModel
    {
        private readonly IMqttService _mqtt;
        private readonly ISpeechService _speech;

        private string _promptText = string.Empty;
        private string _titleText = string.Empty;
        private string _homeText = string.Empty;
        private string _languageLabel = "VI";
        private string? _activeRoomKey;

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
        public string? ActiveRoomKey
        {
            get => _activeRoomKey;
            set => SetProperty(ref _activeRoomKey, value);
        }

        // Localized room names (updated on language change)
        public string RoomWaterIntake => StringIds.NAV_ROOM_WATER_INTAKE.GetString();
        public string RoomChemistryHall => StringIds.NAV_ROOM_CHEMISTRY_HALL.GetString();
        public string RoomRestroom => StringIds.NAV_ROOM_RESTROOM.GetString();
        public string RoomStairs => StringIds.NAV_ROOM_STAIRS.GetString();
        public string RoomRoboticsLab => StringIds.NAV_ROOM_ROBOTICS_LAB.GetString();
        public string RoomElectricalLab => StringIds.NAV_ROOM_ELECTRICAL_LAB.GetString();

        public Command<string> SelectRoomCommand { get; }
        public Command GoHomeCommand { get; }
        public Command ToggleLanguageCommand { get; }

        public NaviViewModel(ILocalizationService localization, IMqttService mqtt, ISpeechService speech)
            : base(localization)
        {
            _mqtt = mqtt;
            _speech = speech;

            SelectRoomCommand = new Command<string>(OnRoomSelected);
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
            TitleText = StringIds.NAV_TITLE.GetString();
            PromptText = StringIds.NAV_WHERE_TO_GO.GetString();
            HomeText = StringIds.NAV_HOME.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();

            OnPropertyChanged(nameof(RoomWaterIntake));
            OnPropertyChanged(nameof(RoomChemistryHall));
            OnPropertyChanged(nameof(RoomRestroom));
            OnPropertyChanged(nameof(RoomStairs));
            OnPropertyChanged(nameof(RoomRoboticsLab));
            OnPropertyChanged(nameof(RoomElectricalLab));
        }

        private async void OnRoomSelected(string roomKey)
        {
            if (ActiveRoomKey == roomKey)
            {
                PromptText = StringIds.NAV_ALREADY_HERE.GetString();
                await _speech.SpeakAsync(PromptText, Localization.CurrentLanguageCode);
                return;
            }

            ActiveRoomKey = roomKey;
            var roomName = GetRoomDisplayName(roomKey);

            var headingMsg = StringIds.NAV_HEADING_TO.GetString()
                .Format(("place", roomName));
            PromptText = headingMsg;

            await _speech.SpeakAsync(headingMsg, Localization.CurrentLanguageCode);

            if (!_mqtt.IsConnected)
                await _mqtt.ConnectAsync();

            await _mqtt.PublishGoalAsync(roomKey);
        }

        private void OnArrivalReceived(object? sender, bool arrived)
        {
            if (!arrived) return;
            var roomName = GetRoomDisplayName(ActiveRoomKey ?? "");
            var arrivedMsg = StringIds.NAV_ARRIVED_READY.GetString()
                .Format(("place", roomName));
            PromptText = arrivedMsg;
            _ = _speech.SpeakAsync(arrivedMsg, Localization.CurrentLanguageCode);
            ActiveRoomKey = null;
        }

        public async Task StopSpeechAsync() => await _speech.StopSpeakingAsync();

        private string GetRoomDisplayName(string roomKey) => roomKey switch
        {
            "btn_room_a" => RoomWaterIntake,
            "btn_room_b" => RoomChemistryHall,
            "btn_room_c" => RoomRestroom,
            "btn_room_d" => RoomStairs,
            "btn_room_e" => RoomRoboticsLab,
            "btn_room_f" => RoomElectricalLab,
            _ => roomKey
        };
    }
}
