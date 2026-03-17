using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    public class QnaViewModel : BaseViewModel
    {
        private readonly ISpeechService _speech;

        private string _promptText = string.Empty;
        private string _titleText = string.Empty;
        private string _homeText = string.Empty;
        private string _languageLabel = "VI";
        private bool _isMicActive;
        private bool _isListening;

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
        public bool IsMicActive
        {
            get => _isMicActive;
            set => SetProperty(ref _isMicActive, value);
        }
        public bool IsListening
        {
            get => _isListening;
            set => SetProperty(ref _isListening, value);
        }

        public Command ToggleMicCommand { get; }
        public Command GoHomeCommand { get; }
        public Command ToggleLanguageCommand { get; }

        private CancellationTokenSource? _listenCts;

        public QnaViewModel(ILocalizationService localization, ISpeechService speech) : base(localization)
        {
            _speech = speech;
            ToggleMicCommand = new Command(OnToggleMic);
            GoHomeCommand = new Command(async () =>
            {
                _listenCts?.Cancel();
                await _speech.StopSpeakingAsync();
                await Shell.Current.GoToAsync("//main");
            });
            ToggleLanguageCommand = new Command(OnToggleLanguage);
            RefreshLocalizedProperties();
        }

        protected override void RefreshLocalizedProperties()
        {
            TitleText = StringIds.QNA_TITLE.GetString();
            PromptText = StringIds.QNA_TAP_MICROPHONE.GetString();
            HomeText = StringIds.QNA_HOME.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();
        }

        private async void OnToggleMic()
        {
            if (IsListening)
            {
                _listenCts?.Cancel();
                IsListening = false;
                IsMicActive = false;
                PromptText = StringIds.QNA_TAP_MICROPHONE.GetString();
                return;
            }

            IsListening = true;
            IsMicActive = true;
            PromptText = StringIds.QNA_LISTENING.GetString();
            _listenCts = new CancellationTokenSource();

            try
            {
                var transcript = await _speech.ListenAsync(
                    Localization.CurrentLanguageCode, _listenCts.Token);

                if (string.IsNullOrWhiteSpace(transcript))
                {
                    PromptText = StringIds.ERROR_LISTENING.GetString();
                    return;
                }

                PromptText = StringIds.QNA_FINDING_ANSWER.GetString();

                // Speak back a placeholder response (real AI handled via IResponseService)
                await _speech.SpeakAsync(transcript, Localization.CurrentLanguageCode);
                PromptText = transcript;
            }
            catch (OperationCanceledException) { }
            catch (Exception ex)
            {
                PromptText = StringIds.ERROR_SOMETHING_WRONG.GetString();
                System.Diagnostics.Debug.WriteLine($"[QnaVM] {ex.Message}");
            }
            finally
            {
                IsListening = false;
                IsMicActive = false;
            }
        }

        public async Task StopAllAsync()
        {
            _listenCts?.Cancel();
            await _speech.StopSpeakingAsync();
        }

        private void OnToggleLanguage()
        {
            Localization.ToggleLanguage();
        }
    }
}
