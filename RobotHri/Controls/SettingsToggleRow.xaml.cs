namespace RobotHri.Controls
{
    /// <summary>
    /// Settings row with a label on the left and a state-pill + Switch on the right.
    /// <see cref="IsOn"/> is TwoWay bindable; the pill text switches between
    /// <see cref="OnText"/> and <see cref="OffText"/> automatically.
    /// </summary>
    public partial class SettingsToggleRow : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsToggleRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsToggleRow)b).LabelView.Text = (string)n);

        public static readonly BindableProperty OnTextProperty =
            BindableProperty.Create(nameof(OnText), typeof(string), typeof(SettingsToggleRow), "On",
                propertyChanged: (b, _, n) => { var r = (SettingsToggleRow)b; if (r.IsOn) r.StateLabel.Text = (string)n; });

        public static readonly BindableProperty OffTextProperty =
            BindableProperty.Create(nameof(OffText), typeof(string), typeof(SettingsToggleRow), "Off",
                propertyChanged: (b, _, n) => { var r = (SettingsToggleRow)b; if (!r.IsOn) r.StateLabel.Text = (string)n; });

        public static readonly BindableProperty DescriptionTextProperty =
            BindableProperty.Create(nameof(DescriptionText), typeof(string), typeof(SettingsToggleRow), string.Empty,
                propertyChanged: (b, _, n) =>
                {
                    var row = (SettingsToggleRow)b;
                    var text = (string)n;
                    row.DescView.Text = text;
                    row.DescView.IsVisible = !string.IsNullOrEmpty(text);
                });

        public static readonly BindableProperty IsOnProperty =
            BindableProperty.Create(nameof(IsOn), typeof(bool), typeof(SettingsToggleRow), true,
                BindingMode.TwoWay,
                propertyChanged: (b, _, n) =>
                {
                    var row = (SettingsToggleRow)b;
                    if (!row._updatingFromSwitch)
                        row.ToggleSwitch.IsToggled = (bool)n;
                    row.ApplyState((bool)n);
                });

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string LabelText       { get => (string)GetValue(LabelTextProperty);       set => SetValue(LabelTextProperty, value); }
        public string DescriptionText { get => (string)GetValue(DescriptionTextProperty); set => SetValue(DescriptionTextProperty, value); }
        public string OnText          { get => (string)GetValue(OnTextProperty);          set => SetValue(OnTextProperty, value); }
        public string OffText         { get => (string)GetValue(OffTextProperty);         set => SetValue(OffTextProperty, value); }
        public bool   IsOn            { get => (bool)GetValue(IsOnProperty);              set => SetValue(IsOnProperty, value); }

        private bool _updatingFromSwitch;

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsToggleRow()
        {
            InitializeComponent();

            LabelView.Text = LabelText;
            DescView.IsVisible = !string.IsNullOrEmpty(DescriptionText);
            ApplyState(IsOn);

            ToggleSwitch.Toggled += (_, e) =>
            {
                _updatingFromSwitch = true;
                IsOn = e.Value;
                _updatingFromSwitch = false;
                ApplyState(e.Value);
            };
        }

        // ─── Visual state ─────────────────────────────────────────────────────────

        private void ApplyState(bool isOn)
        {
            StateLabel.Text = isOn ? OnText : OffText;
            StatePill.BackgroundColor = isOn
                ? GetColor("PrimaryDarkBlue")
                : GetColor("LightBlue");
            StateLabel.TextColor = isOn
                ? GetColor("TextOnPrimary")
                : GetColor("TextDark");
        }

        private static Color GetColor(string key) =>
            Application.Current?.Resources.TryGetValue(key, out var v) == true
                ? (Color)v : Colors.Gray;
    }
}
