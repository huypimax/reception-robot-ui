using System.Windows.Input;

namespace RobotHri.Controls
{
    /// <summary>
    /// Vertical icon + label button for selecting a delivery mode.
    /// Selected state: blue icon, bold blue label, visible underline.
    /// </summary>
    public partial class SettingsModeButton : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty IconTextProperty =
            BindableProperty.Create(nameof(IconText), typeof(string), typeof(SettingsModeButton), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsModeButton)b).IconLabel.Text = (string)n);

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsModeButton), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsModeButton)b).TextLabel.Text = (string)n);

        public static readonly BindableProperty IsSelectedProperty =
            BindableProperty.Create(nameof(IsSelected), typeof(bool), typeof(SettingsModeButton), false,
                propertyChanged: (b, _, n) => ((SettingsModeButton)b).ApplySelectedState((bool)n));

        public static readonly BindableProperty CommandProperty =
            BindableProperty.Create(nameof(Command), typeof(ICommand), typeof(SettingsModeButton));

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string    IconText   { get => (string)GetValue(IconTextProperty);    set => SetValue(IconTextProperty, value); }
        public string    LabelText  { get => (string)GetValue(LabelTextProperty);   set => SetValue(LabelTextProperty, value); }
        public bool      IsSelected { get => (bool)GetValue(IsSelectedProperty);    set => SetValue(IsSelectedProperty, value); }
        public ICommand? Command    { get => (ICommand?)GetValue(CommandProperty);  set => SetValue(CommandProperty, value); }

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsModeButton()
        {
            InitializeComponent();

            IconLabel.Text = IconText;
            TextLabel.Text = LabelText;
            ApplySelectedState(IsSelected);

            ModeTap.Tapped += (_, _) => Command?.Execute(null);
        }

        // ─── Visual state ─────────────────────────────────────────────────────────

        private void ApplySelectedState(bool selected)
        {
            var active  = GetColor("PrimaryDarkBlue");
            var muted   = GetColor("TextMuted");

            IconLabel.TextColor  = selected ? active : muted;
            TextLabel.TextColor  = selected ? active : muted;
            TextLabel.FontFamily = selected ? "RobotoBold" : "RobotoRegular";
            Underline.IsVisible  = selected;
        }

        private static Color GetColor(string key) =>
            Application.Current?.Resources.TryGetValue(key, out var v) == true
                ? (Color)v : Colors.Gray;
    }
}
