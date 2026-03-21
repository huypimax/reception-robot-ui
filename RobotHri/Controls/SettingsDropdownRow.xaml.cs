using System.Windows.Input;

namespace RobotHri.Controls
{
    /// <summary>
    /// Settings row that shows a label (+ optional description) on the left and the current
    /// selected value with an icon on the right. Executes <see cref="Command"/> when tapped.
    /// </summary>
    public partial class SettingsDropdownRow : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsDropdownRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsDropdownRow)b).LabelView.Text = (string)n);

        public static readonly BindableProperty DescriptionTextProperty =
            BindableProperty.Create(nameof(DescriptionText), typeof(string), typeof(SettingsDropdownRow), string.Empty,
                propertyChanged: (b, _, n) =>
                {
                    var row = (SettingsDropdownRow)b;
                    var text = (string)n;
                    row.DescView.Text = text;
                    row.DescView.IsVisible = !string.IsNullOrEmpty(text);
                });

        public static readonly BindableProperty SelectedValueProperty =
            BindableProperty.Create(nameof(SelectedValue), typeof(string), typeof(SettingsDropdownRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsDropdownRow)b).ValueView.Text = (string)n);

        public static readonly BindableProperty CommandProperty =
            BindableProperty.Create(nameof(Command), typeof(ICommand), typeof(SettingsDropdownRow));

        // Icon source for the right-side icon. If null/empty, a default image is used.
        public static readonly BindableProperty IconSourceProperty =
            BindableProperty.Create(nameof(IconSource), typeof(string), typeof(SettingsDropdownRow), null,
                propertyChanged: (b, _, n) => ((SettingsDropdownRow)b).UpdateIcon((string?)n));

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string   LabelText       { get => (string)GetValue(LabelTextProperty);       set => SetValue(LabelTextProperty, value); }
        public string   DescriptionText { get => (string)GetValue(DescriptionTextProperty); set => SetValue(DescriptionTextProperty, value); }
        public string   SelectedValue   { get => (string)GetValue(SelectedValueProperty);   set => SetValue(SelectedValueProperty, value); }
        public ICommand? Command        { get => (ICommand?)GetValue(CommandProperty);       set => SetValue(CommandProperty, value); }
        public string?  IconSource      { get => (string?)GetValue(IconSourceProperty);    set => SetValue(IconSourceProperty, value); }

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsDropdownRow()
        {
            InitializeComponent();

            LabelView.Text = LabelText;
            DescView.IsVisible = !string.IsNullOrEmpty(DescriptionText);
            ValueView.Text = SelectedValue;

            RowTap.Tapped += (_, _) => Command?.Execute(null);
        }

        private void UpdateIcon(string? source)
        {
            const string defaultIcon = "icon_angle_down.png";

            var finalSource = string.IsNullOrEmpty(source) ? defaultIcon : source;

            IconView.Source = finalSource;
            IconView.IsVisible = true;
        }
    }
}
