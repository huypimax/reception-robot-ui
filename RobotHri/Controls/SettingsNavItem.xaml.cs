using System.Windows.Input;

namespace RobotHri.Controls
{
    /// <summary>
    /// Sidebar navigation item for the Settings page.
    /// Shows an icon (emoji/char) + label text.
    /// When IsSelected = true, switches to a PrimaryDarkBlue filled pill with white text.
    /// </summary>
    public partial class SettingsNavItem : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty IconTextProperty =
            BindableProperty.Create(nameof(IconText), typeof(string), typeof(SettingsNavItem), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsNavItem)b).IconLabel.Text = (string)n);

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsNavItem), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsNavItem)b).TextLabel.Text = (string)n);

        public static readonly BindableProperty IsSelectedProperty =
            BindableProperty.Create(nameof(IsSelected), typeof(bool), typeof(SettingsNavItem), false,
                propertyChanged: (b, _, n) => ((SettingsNavItem)b).ApplySelectedState((bool)n));

        public static readonly BindableProperty CommandProperty =
            BindableProperty.Create(nameof(Command), typeof(ICommand), typeof(SettingsNavItem));

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string  IconText   { get => (string)GetValue(IconTextProperty);    set => SetValue(IconTextProperty, value); }
        public string  LabelText  { get => (string)GetValue(LabelTextProperty);   set => SetValue(LabelTextProperty, value); }
        public bool    IsSelected { get => (bool)GetValue(IsSelectedProperty);    set => SetValue(IsSelectedProperty, value); }
        public ICommand? Command  { get => (ICommand?)GetValue(CommandProperty);  set => SetValue(CommandProperty, value); }

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsNavItem()
        {
            InitializeComponent();

            IconLabel.Text = IconText;
            TextLabel.Text = LabelText;

            ItemTap.Tapped += (_, _) => Command?.Execute(null);
        }

        // ─── Visual state ─────────────────────────────────────────────────────────

        private void ApplySelectedState(bool selected)
        {
            SelectionBg.BackgroundColor = selected
                ? GetColor("PrimaryDarkBlue")
                : Colors.Transparent;

            var textColor = selected
                ? GetColor("TextOnPrimary")
                : GetColor("TextDark");

            IconLabel.TextColor = textColor;
            TextLabel.TextColor = textColor;

            TextLabel.FontFamily = selected ? "RobotoBold" : "RobotoRegular";
        }

        private static Color GetColor(string key) =>
            Application.Current?.Resources.TryGetValue(key, out var v) == true
                ? (Color)v : Colors.Black;
    }
}
