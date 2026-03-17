using RobotHri.Languages;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    public class MainViewModel : BaseViewModel
    {
        private string _welcomeText = string.Empty;
        private string _titleText = string.Empty;
        private string _btnQna = string.Empty;
        private string _btnNavigation = string.Empty;
        private string _btnLab = string.Empty;
        private string _btnDelivery = string.Empty;
        private string _btnCheckin = string.Empty;
        private string _languageLabel = "VI";

        public string WelcomeText
        {
            get => _welcomeText;
            set => SetProperty(ref _welcomeText, value);
        }
        public string TitleText
        {
            get => _titleText;
            set => SetProperty(ref _titleText, value);
        }
        public string BtnQna
        {
            get => _btnQna;
            set => SetProperty(ref _btnQna, value);
        }
        public string BtnNavigation
        {
            get => _btnNavigation;
            set => SetProperty(ref _btnNavigation, value);
        }
        public string BtnLab
        {
            get => _btnLab;
            set => SetProperty(ref _btnLab, value);
        }
        public string BtnDelivery
        {
            get => _btnDelivery;
            set => SetProperty(ref _btnDelivery, value);
        }
        public string BtnCheckin
        {
            get => _btnCheckin;
            set => SetProperty(ref _btnCheckin, value);
        }
        public string LanguageLabel
        {
            get => _languageLabel;
            set => SetProperty(ref _languageLabel, value);
        }

        public Command ToggleLanguageCommand { get; }
        public Command NavigateQnaCommand { get; }
        public Command NavigateNaviCommand { get; }
        public Command NavigateLabCommand { get; }
        public Command NavigateDeliCommand { get; }
        public Command NavigateCheckinCommand { get; }

        public MainViewModel(ILocalizationService localization) : base(localization)
        {
            ToggleLanguageCommand = new Command(OnToggleLanguage);
            NavigateQnaCommand = new Command(async () => await Shell.Current.GoToAsync("//qna"));
            NavigateNaviCommand = new Command(async () => await Shell.Current.GoToAsync("//navi"));
            NavigateLabCommand = new Command(async () => await Shell.Current.GoToAsync("//lab"));
            NavigateDeliCommand = new Command(async () => await Shell.Current.GoToAsync("//deli"));
            NavigateCheckinCommand = new Command(async () =>
                await Shell.Current.DisplayAlert("Check-in", "Coming soon", "OK"));

            RefreshLocalizedProperties();
        }

        protected override void RefreshLocalizedProperties()
        {
            WelcomeText = GetWelcomeGreeting();
            TitleText = StringIds.MAIN_TITLE.GetString();
            BtnQna = StringIds.MAIN_QNA.GetString();
            BtnNavigation = StringIds.MAIN_NAVIGATION.GetString();
            BtnLab = StringIds.MAIN_LAB.GetString();
            BtnDelivery = StringIds.MAIN_DELIVERY.GetString();
            BtnCheckin = StringIds.MAIN_CHECKIN.GetString();
            LanguageLabel = Localization.GetCurrentLanguageName();
        }

        private string GetWelcomeGreeting()
        {
            var hour = DateTime.Now.Hour;
            string timeGreeting = hour switch
            {
                < 12 => StringIds.WELCOME_GOOD_MORNING.GetString(),
                < 18 => StringIds.WELCOME_GOOD_AFTERNOON.GetString(),
                _ => StringIds.WELCOME_GOOD_EVENING.GetString()
            };
            var greeting = StringIds.WELCOME_GREETING.GetString();
            return $"{timeGreeting}! {greeting}";
        }

        private void OnToggleLanguage()
        {
            Localization.ToggleLanguage();
        }
    }
}
