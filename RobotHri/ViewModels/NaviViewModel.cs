using RobotHri.Languages;
using RobotHri.Services;
using System.Threading;
using System.Windows.Input;

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
        private bool _isBusy;
        private string _loadingMessage = string.Empty;

#if DEBUG
        // Set to false to rely only on real MQTT robot/arrival messages.
        private const bool SimulateRobotArrivalAfterPublish = true;
        private static readonly TimeSpan SimulatedArrivalDelay = TimeSpan.FromMinutes(0.2);
        private CancellationTokenSource? _simulatedArrivalCts;
#endif

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

        public bool IsBusy
        {
            get => _isBusy;
            set => SetProperty(ref _isBusy, value);
        }

        public string LoadingMessage
        {
            get => _loadingMessage;
            set => SetProperty(ref _loadingMessage, value);
        }

        // Localized room names (updated on language change)
        public string RoomWaterIntake => StringIds.NAV_ROOM_WATER_INTAKE.GetString();
        public string RoomChemistryHall => StringIds.NAV_ROOM_CHEMISTRY_HALL.GetString();
        public string RoomRestroom => StringIds.NAV_ROOM_RESTROOM.GetString();
        public string RoomStairs => StringIds.NAV_ROOM_STAIRS.GetString();
        public string RoomRoboticsLab => StringIds.NAV_ROOM_ROBOTICS_LAB.GetString();
        public string RoomElectricalLab => StringIds.NAV_ROOM_ELECTRICAL_LAB.GetString();

        public ICommand SelectRoomCommand { get; }
        public ICommand GoHomeCommand { get; }
        public ICommand ToggleLanguageCommand { get; }
        public ICommand CancelNavigationCommand { get; }

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

            CancelNavigationCommand = new Command(OnCancelNavigation);

            _mqtt.ArrivalReceived += OnArrivalReceived;
            RefreshLocalizedProperties();

            Task.Run(async () =>
            {
                if (!_mqtt.IsConnected)
                {
                    var connected = await _mqtt.ConnectAsync();
                    if (!connected)
                    {
                        IsBusy = false;
                        ActiveRoomKey = null;
                        LoadingMessage = string.Empty;
                        PromptText = StringIds.NAV_WHERE_TO_GO.GetString();

                        if (Application.Current?.MainPage != null)
                        {
                            await Application.Current.MainPage.DisplayAlert(
                                StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString(),
                                StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString(),
                                StringIds.OK.GetString());
                        }

                        return;
                    }
                }
            });
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
            if (IsBusy) return;

            if (ActiveRoomKey == roomKey)
            {
                PromptText = StringIds.NAV_ALREADY_HERE.GetString();
                await _speech.SpeakAsync(PromptText, Localization.CurrentLanguageCode);
                return;
            }

            IsBusy = true;
            ActiveRoomKey = roomKey;

            var localizedPlace = GetLocalizedRoomName(roomKey);
            var headingMsg = StringIds.NAV_HEADING_TO.GetString()
                .Format(("place", localizedPlace));

            PromptText = headingMsg;
            LoadingMessage = headingMsg;

            await _speech.SpeakAsync(headingMsg, Localization.CurrentLanguageCode);

            if (!_mqtt.IsConnected)
            {
                var connected = await _mqtt.ConnectAsync();
                if (!connected)
                {
                    IsBusy = false;
                    ActiveRoomKey = null;
                    LoadingMessage = string.Empty;
                    PromptText = StringIds.NAV_WHERE_TO_GO.GetString();

                    if (Application.Current?.MainPage != null)
                    {
                        await Application.Current.MainPage.DisplayAlert(
                            StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString(),
                            StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString(),
                            StringIds.OK.GetString());
                    }

                    return;
                }
            }

            await _mqtt.PublishGoalAsync(GetRobotGoalPlace(roomKey));

#if DEBUG
            if (SimulateRobotArrivalAfterPublish)
                StartSimulatedArrivalForTesting(roomKey);
#endif
        }

#if DEBUG
        private void CancelSimulatedArrival()
        {
            try
            {
                _simulatedArrivalCts?.Cancel();
            }
            catch (ObjectDisposedException) { /* ignore */ }

            _simulatedArrivalCts?.Dispose();
            _simulatedArrivalCts = null;
        }

        private void StartSimulatedArrivalForTesting(string roomKeySnapshot)
        {
            CancelSimulatedArrival();
            _simulatedArrivalCts = new CancellationTokenSource();
            var ct = _simulatedArrivalCts.Token;
            _ = RunSimulatedArrivalAsync(roomKeySnapshot, ct);
        }

        private async Task RunSimulatedArrivalAsync(string roomKeySnapshot, CancellationToken ct)
        {
            try
            {
                await Task.Delay(SimulatedArrivalDelay, ct).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                return;
            }

            await MainThread.InvokeOnMainThreadAsync(() =>
            {
                if (!IsBusy || ActiveRoomKey != roomKeySnapshot)
                    return Task.CompletedTask;
                _ = HandleArrivalAsync();
                return Task.CompletedTask;
            });
        }
#endif

        private async void ConnectMQTT()
        {
            if (!_mqtt.IsConnected)
            {
                var connected = await _mqtt.ConnectAsync();
                if (!connected)
                {
                    IsBusy = false;
                    ActiveRoomKey = null;
                    LoadingMessage = string.Empty;
                    PromptText = StringIds.NAV_WHERE_TO_GO.GetString();

                    if (Application.Current?.MainPage != null)
                    {
                        await Application.Current.MainPage.DisplayAlert(
                            StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString(),
                            StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString(),
                            StringIds.OK.GetString());
                    }

                    return;
                }
            }
        }

        private async void OnCancelNavigation()
        {
            if (!IsBusy) return;

#if DEBUG
            CancelSimulatedArrival();
#endif
            IsBusy = false;
            ActiveRoomKey = null;
            LoadingMessage = string.Empty;
            PromptText = StringIds.NAV_WHERE_TO_GO.GetString(); // Reset prompt

            await _speech.StopSpeakingAsync();

            // Optional: Publish a "cancel" or "stop" message to MQTT if your robot supports it.
            // Example: await _mqtt.PublishGoalAsync("stop");
        }

        private void OnArrivalReceived(object? sender, bool arrived)
        {
            if (!arrived) return;
#if DEBUG
            CancelSimulatedArrival();
#endif
            _ = HandleArrivalAsync();
        }

        private async Task HandleArrivalAsync()
        {
            IsBusy = false;
            var roomName = GetLocalizedRoomName(ActiveRoomKey ?? string.Empty);
            var arrivedMsg = StringIds.NAV_ARRIVED_READY.GetString()
                .Format(("place", roomName));

            PromptText = arrivedMsg;
            LoadingMessage = string.Empty;

            await _speech.SpeakAsync(arrivedMsg, Localization.CurrentLanguageCode);

            if (Application.Current?.MainPage != null)
            {
                await Application.Current.MainPage.DisplayAlert(
                    StringIds.NAV_ARRIVAL_TITLE.GetString(),
                    arrivedMsg,
                    StringIds.OK.GetString()
                );
            }

            ActiveRoomKey = null;
        }

        public async Task StopSpeechAsync() => await _speech.StopSpeakingAsync();

        // Localized label for prompts, loading overlay, and TTS.
        private static string GetLocalizedRoomName(string roomKey) => roomKey switch
        {
            "RoomWaterIntake" => StringIds.NAV_ROOM_WATER_INTAKE.GetString(),
            "RoomChemistryHall" => StringIds.NAV_ROOM_CHEMISTRY_HALL.GetString(),
            "RoomRestroom" => StringIds.NAV_ROOM_RESTROOM.GetString(),
            "RoomStairs" => StringIds.NAV_ROOM_STAIRS.GetString(),
            "RoomRoboticsLab" => StringIds.NAV_ROOM_ROBOTICS_LAB.GetString(),
            "RoomElectricalLab" => StringIds.NAV_ROOM_ELECTRICAL_LAB.GetString(),
            _ => roomKey
        };

        // English place names for MQTT (matches Python PLACE_BUTTON_PAIRS).
        private static string GetRobotGoalPlace(string roomKey) => roomKey switch
        {
            "RoomWaterIntake" => "Water Intake",
            "RoomChemistryHall" => "Chemistry Hall",
            "RoomRestroom" => "Restroom",
            "RoomStairs" => "Stairs",
            "RoomRoboticsLab" => "Robotics Lab",
            "RoomElectricalLab" => "Electrical Lab",
            _ => roomKey
        };
    }
}
