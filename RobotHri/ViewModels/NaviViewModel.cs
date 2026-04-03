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
        private static readonly TimeSpan SimulatedArrivalDelay = TimeSpan.FromMinutes(0.1);
        private CancellationTokenSource? _simulatedArrivalCts;
#endif

        // Auto-dismiss cancellation tokens
        private CancellationTokenSource? _autoDismissCts;
        private CancellationTokenSource? _locationInfoDismissCts;

        // Generic Notification Popup State
        private bool _isNotificationPopupVisible;
        private string _notificationMessage = string.Empty;
        private string _notificationTitle = string.Empty;
        private string _okButtonText = string.Empty;
        private bool _isShowingLocationInfo;
        private string? _lastArrivedRoomKey;

        // Error Popup State
        private bool _isErrorPopupVisible;
        private string _errorMessage = string.Empty;
        private string _errorTitle = string.Empty;

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

        public bool IsNotificationPopupVisible
        {
            get => _isNotificationPopupVisible;
            set => SetProperty(ref _isNotificationPopupVisible, value);
        }

        public string NotificationMessage
        {
            get => _notificationMessage;
            set => SetProperty(ref _notificationMessage, value);
        }

        public string NotificationTitle
        {
            get => _notificationTitle;
            set => SetProperty(ref _notificationTitle, value);
        }

        public string OkButtonText
        {
            get => _okButtonText;
            set => SetProperty(ref _okButtonText, value);
        }

        public bool IsErrorPopupVisible
        {
            get => _isErrorPopupVisible;
            set => SetProperty(ref _isErrorPopupVisible, value);
        }

        public string ErrorMessage
        {
            get => _errorMessage;
            set => SetProperty(ref _errorMessage, value);
        }

        public string ErrorTitle
        {
            get => _errorTitle;
            set => SetProperty(ref _errorTitle, value);
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
        public ICommand DismissNotificationCommand { get; }
        public ICommand DismissErrorPopupCommand { get; }

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

            DismissNotificationCommand = new Command(() =>
            {
                if (!_isShowingLocationInfo)
                {
                    // If we were showing the arrival popup, cancel the 10s timer and show the location info
                    CancelAutoDismiss();
                    ShowLocationInfoPopup();
                }
                else
                {
                    // If we were showing the location info, just dismiss it and cancel its 2m timer
                    CancelLocationInfoAutoDismiss();
                    IsNotificationPopupVisible = false;
                    _isShowingLocationInfo = false;
                    _lastArrivedRoomKey = null;
                }
            });

            DismissErrorPopupCommand = new Command(() => IsErrorPopupVisible = false);

            RefreshLocalizedProperties();

            Task.Run(async () =>
            {
                if (!_mqtt.IsConnected)
                {
                    var connected = await _mqtt.ConnectAsync();
                    if (!connected)
                    {
                        // Ensure UI updates happen on main thread
                        await MainThread.InvokeOnMainThreadAsync(() =>
                        {
                            IsBusy = false;
                            ActiveRoomKey = null;
                            LoadingMessage = string.Empty;
                            PromptText = StringIds.NAV_WHERE_TO_GO.GetString();

                            ErrorTitle = StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString();
                            ErrorMessage = StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString();
                            IsErrorPopupVisible = true;
                        });
                    }
                }
            });
        }

        public void AttachMqttHandlers()
        {
            _mqtt.ArrivalReceived -= OnArrivalReceived; // Ensure no duplicates
            _mqtt.ArrivalReceived += OnArrivalReceived;
        }

        public void DetachMqttHandlers()
        {
            _mqtt.ArrivalReceived -= OnArrivalReceived;
        }

        protected override void RefreshLocalizedProperties()
        {
            TitleText = StringIds.NAV_TITLE.GetString();
            PromptText = StringIds.NAV_WHERE_TO_GO.GetString();
            HomeText = StringIds.NAV_HOME.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();
            OkButtonText = StringIds.OK.GetString();

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

            // Clear any active popups or timers when starting a new navigation
            IsNotificationPopupVisible = false;
            CancelAutoDismiss();
            CancelLocationInfoAutoDismiss();
            _isShowingLocationInfo = false;
            _lastArrivedRoomKey = null;

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

                    ErrorTitle = StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString();
                    ErrorMessage = StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString();
                    IsErrorPopupVisible = true;

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

            // Must jump to main thread
            _ = MainThread.InvokeOnMainThreadAsync(() =>
            {
                if (!IsBusy || ActiveRoomKey != roomKeySnapshot)
                    return Task.CompletedTask;

                return HandleArrivalAsync();
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

                    ErrorTitle = StringIds.NAV_MQTT_CONNECT_FAILED_TITLE.GetString();
                    ErrorMessage = StringIds.NAV_MQTT_CONNECT_FAILED_MESSAGE.GetString();
                    IsErrorPopupVisible = true;
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
            _lastArrivedRoomKey = null;
            _isShowingLocationInfo = false;
            IsNotificationPopupVisible = false;

            CancelAutoDismiss();
            CancelLocationInfoAutoDismiss();

            LoadingMessage = string.Empty;
            PromptText = StringIds.NAV_WHERE_TO_GO.GetString();

            await _speech.StopSpeakingAsync();
        }

        private async void OnArrivalReceived(object? sender, bool arrived)
        {
            if (!arrived) return;
#if DEBUG
            CancelSimulatedArrival();
#endif
            // Event handlers MUST await HandleArrivalAsync to execute correctly
            await HandleArrivalAsync();
        }

        private async Task HandleArrivalAsync()
        {
            // Must update UI on the main thread
            await MainThread.InvokeOnMainThreadAsync(async () =>
            {
                IsBusy = false;
                _lastArrivedRoomKey = ActiveRoomKey; // Save the room key for the location info popup

                var roomName = GetLocalizedRoomName(_lastArrivedRoomKey ?? string.Empty);
                var arrivedMsg = StringIds.NAV_ARRIVED_READY.GetString()
                    .Format(("place", roomName));

                PromptText = arrivedMsg;
                LoadingMessage = string.Empty;

                _isShowingLocationInfo = false;
                NotificationTitle = StringIds.NAV_ARRIVAL_TITLE.GetString();
                NotificationMessage = arrivedMsg;
                IsNotificationPopupVisible = true;

                await _speech.SpeakAsync(arrivedMsg, Localization.CurrentLanguageCode);
                ActiveRoomKey = null;

                StartAutoDismissTimer();
            });
        }

        private void ShowLocationInfoPopup()
        {
            if (string.IsNullOrEmpty(_lastArrivedRoomKey))
            {
                IsNotificationPopupVisible = false;
                return;
            }

            _isShowingLocationInfo = true;

            // Set title to room name and message to room description
            NotificationTitle = GetLocalizedRoomName(_lastArrivedRoomKey);
            NotificationMessage = GetRoomDescription(_lastArrivedRoomKey);

            // Keep it visible (it just updates the text seamlessly)
            IsNotificationPopupVisible = true;

            StartLocationInfoAutoDismissTimer();
        }

        private void CancelAutoDismiss()
        {
            try
            {
                _autoDismissCts?.Cancel();
            }
            catch (ObjectDisposedException) { /* ignore */ }

            _autoDismissCts?.Dispose();
            _autoDismissCts = null;
        }

        private void StartAutoDismissTimer()
        {
            CancelAutoDismiss();
            _autoDismissCts = new CancellationTokenSource();
            var ct = _autoDismissCts.Token;

            Task.Run(async () =>
            {
                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(10), ct);

                    if (!ct.IsCancellationRequested)
                    {
                        await MainThread.InvokeOnMainThreadAsync(() =>
                        {
                            // If 10 seconds pass, transition to Location Info automatically
                            ShowLocationInfoPopup();
                        });
                    }
                }
                catch (OperationCanceledException)
                {
                    // Timer was cancelled because user clicked OK
                }
            }, ct);
        }

        private void CancelLocationInfoAutoDismiss()
        {
            try
            {
                _locationInfoDismissCts?.Cancel();
            }
            catch (ObjectDisposedException) { /* ignore */ }

            _locationInfoDismissCts?.Dispose();
            _locationInfoDismissCts = null;
        }

        private void StartLocationInfoAutoDismissTimer()
        {
            CancelLocationInfoAutoDismiss();
            _locationInfoDismissCts = new CancellationTokenSource();
            var ct = _locationInfoDismissCts.Token;

            Task.Run(async () =>
            {
                try
                {
                    await Task.Delay(TimeSpan.FromMinutes(2), ct);

                    if (!ct.IsCancellationRequested)
                    {
                        await MainThread.InvokeOnMainThreadAsync(() =>
                        {
                            // Auto dismiss the location info after 2 minutes
                            IsNotificationPopupVisible = false;
                            _isShowingLocationInfo = false;
                            _lastArrivedRoomKey = null;
                        });
                    }
                }
                catch (OperationCanceledException)
                {
                    // Cancelled manually by user
                }
            }, ct);
        }

        public async Task StopSpeechAsync() => await _speech.StopSpeakingAsync();

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

        private static string GetRoomDescription(string roomKey) => roomKey switch
        {
            "RoomRoboticsLab" => StringIds.LAB_DEVICE_PLC.GetString(),
            "RoomElectricalLab" => StringIds.LAB_DEVICE_IFM.GetString(),
            "RoomChemistryHall" => StringIds.LAB_DEVICE_STEP.GetString(),
            "RoomWaterIntake" => StringIds.LAB_DEVICE_HMI.GetString(),
            _ => StringIds.LAB_PROMPT.GetString()
        };
    }
}
