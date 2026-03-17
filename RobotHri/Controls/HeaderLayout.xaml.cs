namespace RobotHri.Controls
{
    /// <summary>
    /// Reusable page header with title, optional back button, and language toggle.
    /// Used on every page of the app.
    /// </summary>
    public partial class HeaderLayout : ContentView
    {
        public static readonly BindableProperty TitleProperty =
            BindableProperty.Create(nameof(Title), typeof(string), typeof(HeaderLayout), string.Empty,
                propertyChanged: (b, o, n) => ((HeaderLayout)b).TitleLabel.Text = (string)n);

        public static readonly BindableProperty BackTextProperty =
            BindableProperty.Create(nameof(BackText), typeof(string), typeof(HeaderLayout), "Home",
                propertyChanged: (b, o, n) => ((HeaderLayout)b).BackLabel.Text = (string)n);

        public static readonly BindableProperty ShowBackButtonProperty =
            BindableProperty.Create(nameof(ShowBackButton), typeof(bool), typeof(HeaderLayout), false,
                propertyChanged: (b, o, n) => ((HeaderLayout)b).BackButton.IsVisible = (bool)n);

        public static readonly BindableProperty LanguageLabelTextProperty =
            BindableProperty.Create(nameof(LanguageLabelText), typeof(string), typeof(HeaderLayout), "VI",
                propertyChanged: (b, o, n) => ((HeaderLayout)b).LanguageLabel.Text = (string)n);

        public string Title
        {
            get => (string)GetValue(TitleProperty);
            set => SetValue(TitleProperty, value);
        }

        public string BackText
        {
            get => (string)GetValue(BackTextProperty);
            set => SetValue(BackTextProperty, value);
        }

        public bool ShowBackButton
        {
            get => (bool)GetValue(ShowBackButtonProperty);
            set => SetValue(ShowBackButtonProperty, value);
        }

        public string LanguageLabelText
        {
            get => (string)GetValue(LanguageLabelTextProperty);
            set => SetValue(LanguageLabelTextProperty, value);
        }

        public event EventHandler? BackTapped;
        public event EventHandler? LanguageToggled;

        public HeaderLayout()
        {
            InitializeComponent();

            // Sync all labels to their BindableProperty defaults immediately after init.
            // MAUI's propertyChanged callback only fires on VALUE CHANGE, so when the bound
            // ViewModel value equals the BindableProperty default the label is never updated.
            LanguageLabel.Text = LanguageLabelText;
            TitleLabel.Text = Title;
            BackLabel.Text = BackText;
            BackButton.IsVisible = ShowBackButton;

            BackTap.Tapped += (s, e) => BackTapped?.Invoke(this, EventArgs.Empty);
            LanguageTap.Tapped += (s, e) => LanguageToggled?.Invoke(this, EventArgs.Empty);
        }
    }
}
