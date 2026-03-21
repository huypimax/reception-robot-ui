namespace RobotHri.Controls
{
    /// <summary>
    /// Settings row with a label on the left and a [−] [value] [+] integer stepper on the right.
    /// </summary>
    public partial class SettingsStepperRow : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsStepperRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsStepperRow)b).LabelView.Text = (string)n);

        public static readonly BindableProperty ValueProperty =
            BindableProperty.Create(nameof(Value), typeof(int), typeof(SettingsStepperRow), 0,
                BindingMode.TwoWay,
                propertyChanged: (b, _, n) => ((SettingsStepperRow)b).RefreshValueLabel());

        public static readonly BindableProperty MinValueProperty =
            BindableProperty.Create(nameof(MinValue), typeof(int), typeof(SettingsStepperRow), 0);

        public static readonly BindableProperty MaxValueProperty =
            BindableProperty.Create(nameof(MaxValue), typeof(int), typeof(SettingsStepperRow), 100);

        public static readonly BindableProperty StepProperty =
            BindableProperty.Create(nameof(Step), typeof(int), typeof(SettingsStepperRow), 1);

        public static readonly BindableProperty UnitProperty =
            BindableProperty.Create(nameof(Unit), typeof(string), typeof(SettingsStepperRow), string.Empty,
                propertyChanged: (b, _, _2) => ((SettingsStepperRow)b).RefreshValueLabel());

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string LabelText { get => (string)GetValue(LabelTextProperty); set => SetValue(LabelTextProperty, value); }
        public int    Value     { get => (int)GetValue(ValueProperty);         set => SetValue(ValueProperty, value); }
        public int    MinValue  { get => (int)GetValue(MinValueProperty);      set => SetValue(MinValueProperty, value); }
        public int    MaxValue  { get => (int)GetValue(MaxValueProperty);      set => SetValue(MaxValueProperty, value); }
        public int    Step      { get => (int)GetValue(StepProperty);          set => SetValue(StepProperty, value); }
        public string Unit      { get => (string)GetValue(UnitProperty);       set => SetValue(UnitProperty, value); }

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsStepperRow()
        {
            InitializeComponent();

            LabelView.Text = LabelText;
            RefreshValueLabel();

            MinusTap.Tapped += (_, _) =>
            {
                Value = Math.Max(MinValue, Value - Step);
            };

            PlusTap.Tapped += (_, _) =>
            {
                Value = Math.Min(MaxValue, Value + Step);
            };
        }

        // ─── Display ──────────────────────────────────────────────────────────────

        private void RefreshValueLabel()
        {
            ValueLabel.Text = $"{Value}{Unit}";
        }
    }
}
