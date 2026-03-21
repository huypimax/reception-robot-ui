namespace RobotHri.Controls
{
    /// <summary>
    /// Read-only info row: label on the left, value on the right, hairline divider below.
    /// Used in the System Settings network-information panel.
    /// </summary>
    public partial class SettingsInfoRow : ContentView
    {
        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsInfoRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsInfoRow)b).LabelView.Text = (string)n);

        public static readonly BindableProperty ValueProperty =
            BindableProperty.Create(nameof(Value), typeof(string), typeof(SettingsInfoRow), "—",
                propertyChanged: (b, _, n) => ((SettingsInfoRow)b).ValueView.Text = (string)n);

        public string LabelText { get => (string)GetValue(LabelTextProperty); set => SetValue(LabelTextProperty, value); }
        public string Value     { get => (string)GetValue(ValueProperty);     set => SetValue(ValueProperty, value); }

        public SettingsInfoRow()
        {
            InitializeComponent();
            LabelView.Text = LabelText;
            ValueView.Text = Value;
        }
    }
}
