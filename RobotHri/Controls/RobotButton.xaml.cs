namespace RobotHri.Controls
{
    /// <summary>
    /// Primary styled button for Robot HRI. Mirrors CloudBanking's BtnGradient.
    /// Supports Normal (dark blue) and Secondary (outlined) styles.
    /// </summary>
    public partial class RobotButton : ContentView
    {
        public static readonly BindableProperty TextProperty =
            BindableProperty.Create(nameof(Text), typeof(string), typeof(RobotButton), string.Empty,
                propertyChanged: (b, o, n) => ((RobotButton)b).ButtonLabel.Text = (string)n);

        public static readonly BindableProperty CommandProperty =
            BindableProperty.Create(nameof(Command), typeof(Command), typeof(RobotButton));

        public static readonly BindableProperty CommandParameterProperty =
            BindableProperty.Create(nameof(CommandParameter), typeof(object), typeof(RobotButton));

        public static readonly BindableProperty IconSourceProperty =
            BindableProperty.Create(nameof(IconSource), typeof(string), typeof(RobotButton), null,
                propertyChanged: (b, o, n) => ((RobotButton)b).UpdateIcon((string?)n));

        public static readonly BindableProperty ButtonStyleProperty =
            BindableProperty.Create(nameof(ButtonStyle), typeof(RobotButtonStyle), typeof(RobotButton),
                RobotButtonStyle.Primary, propertyChanged: (b, o, n) => ((RobotButton)b).ApplyStyle((RobotButtonStyle)n));

        public string Text
        {
            get => (string)GetValue(TextProperty);
            set => SetValue(TextProperty, value);
        }

        public Command? Command
        {
            get => (Command?)GetValue(CommandProperty);
            set => SetValue(CommandProperty, value);
        }

        public object? CommandParameter
        {
            get => GetValue(CommandParameterProperty);
            set => SetValue(CommandParameterProperty, value);
        }

        public string? IconSource
        {
            get => (string?)GetValue(IconSourceProperty);
            set => SetValue(IconSourceProperty, value);
        }

        public RobotButtonStyle ButtonStyle
        {
            get => (RobotButtonStyle)GetValue(ButtonStyleProperty);
            set => SetValue(ButtonStyleProperty, value);
        }

        public RobotButton()
        {
            InitializeComponent();

            var tapGesture = new TapGestureRecognizer();
            tapGesture.Tapped += OnTapped;
            ButtonBorder.GestureRecognizers.Add(tapGesture);
        }

        private async void OnTapped(object? sender, TappedEventArgs e)
        {
            // Visual feedback (scale pulse)
            await ButtonBorder.ScaleTo(0.95, 80);
            await ButtonBorder.ScaleTo(1.0, 80);

            if (Command?.CanExecute(CommandParameter) == true)
                Command.Execute(CommandParameter);
        }

        private void UpdateIcon(string? source)
        {
            ButtonIcon.IsVisible = !string.IsNullOrEmpty(source);
            if (!string.IsNullOrEmpty(source))
                ButtonIcon.Source = source;
        }

        private void ApplyStyle(RobotButtonStyle style)
        {
            switch (style)
            {
                case RobotButtonStyle.Primary:
                    ButtonBorder.BackgroundColor = Color.FromArgb("#00294D");
                    ButtonLabel.TextColor = Colors.White;
                    ButtonBorder.Stroke = Colors.Transparent;
                    break;
                case RobotButtonStyle.Secondary:
                    ButtonBorder.BackgroundColor = Colors.Transparent;
                    ButtonLabel.TextColor = Color.FromArgb("#00294D");
                    ButtonBorder.Stroke = Color.FromArgb("#00294D");
                    break;
                case RobotButtonStyle.Danger:
                    ButtonBorder.BackgroundColor = Color.FromArgb("#AC0000");
                    ButtonLabel.TextColor = Colors.White;
                    ButtonBorder.Stroke = Colors.Transparent;
                    break;
            }
        }
    }

    public enum RobotButtonStyle
    {
        Primary,
        Secondary,
        Danger
    }
}
