namespace RobotHri.Controls
{
    /// <summary>
    /// Slider row used in the Route Settings panel.
    /// Exposes a two-way <see cref="Value"/> BindableProperty so the parent ViewModel
    /// can read and write the slider position without circular updates.
    /// </summary>
    public partial class SettingsSliderRow : ContentView
    {
        // ─── BindableProperties ───────────────────────────────────────────────────

        public static readonly BindableProperty LabelTextProperty =
            BindableProperty.Create(nameof(LabelText), typeof(string), typeof(SettingsSliderRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).TitleLabel.Text = (string)n);

        public static readonly BindableProperty DescriptionTextProperty =
            BindableProperty.Create(nameof(DescriptionText), typeof(string), typeof(SettingsSliderRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).DescLabel.Text = (string)n);

        public static readonly BindableProperty ValueProperty =
            BindableProperty.Create(nameof(Value), typeof(double), typeof(SettingsSliderRow), 0.0,
                BindingMode.TwoWay,
                propertyChanged: (b, _, n) =>
                {
                    var row = (SettingsSliderRow)b;
                    if (!row._updatingFromSlider)
                        row.SliderControl.Value = (double)n;
                    row.RefreshValueLabel();
                });

        public static readonly BindableProperty MinValueProperty =
            BindableProperty.Create(nameof(MinValue), typeof(double), typeof(SettingsSliderRow), 0.0,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).SliderControl.Minimum = (double)n);

        public static readonly BindableProperty MaxValueProperty =
            BindableProperty.Create(nameof(MaxValue), typeof(double), typeof(SettingsSliderRow), 100.0,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).SliderControl.Maximum = (double)n);

        public static readonly BindableProperty UnitProperty =
            BindableProperty.Create(nameof(Unit), typeof(string), typeof(SettingsSliderRow), string.Empty,
                propertyChanged: (b, _, _2) => ((SettingsSliderRow)b).RefreshValueLabel());

        public static readonly BindableProperty MinLabelProperty =
            BindableProperty.Create(nameof(MinLabel), typeof(string), typeof(SettingsSliderRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).MinLabelView.Text = (string)n);

        public static readonly BindableProperty MaxLabelProperty =
            BindableProperty.Create(nameof(MaxLabel), typeof(string), typeof(SettingsSliderRow), string.Empty,
                propertyChanged: (b, _, n) => ((SettingsSliderRow)b).MaxLabelView.Text = (string)n);

        public static readonly BindableProperty DecimalPlacesProperty =
            BindableProperty.Create(nameof(DecimalPlaces), typeof(int), typeof(SettingsSliderRow), 0,
                propertyChanged: (b, _, _2) => ((SettingsSliderRow)b).RefreshValueLabel());

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public string LabelText       { get => (string)GetValue(LabelTextProperty);        set => SetValue(LabelTextProperty, value); }
        public string DescriptionText { get => (string)GetValue(DescriptionTextProperty);  set => SetValue(DescriptionTextProperty, value); }
        public double Value           { get => (double)GetValue(ValueProperty);             set => SetValue(ValueProperty, value); }
        public double MinValue        { get => (double)GetValue(MinValueProperty);          set => SetValue(MinValueProperty, value); }
        public double MaxValue        { get => (double)GetValue(MaxValueProperty);          set => SetValue(MaxValueProperty, value); }
        public string Unit            { get => (string)GetValue(UnitProperty);              set => SetValue(UnitProperty, value); }
        public string MinLabel        { get => (string)GetValue(MinLabelProperty);          set => SetValue(MinLabelProperty, value); }
        public string MaxLabel        { get => (string)GetValue(MaxLabelProperty);          set => SetValue(MaxLabelProperty, value); }
        public int    DecimalPlaces   { get => (int)GetValue(DecimalPlacesProperty);        set => SetValue(DecimalPlacesProperty, value); }

        private bool _updatingFromSlider;

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SettingsSliderRow()
        {
            InitializeComponent();

            TitleLabel.Text   = LabelText;
            DescLabel.Text    = DescriptionText;
            MinLabelView.Text = MinLabel;
            MaxLabelView.Text = MaxLabel;
            RefreshValueLabel();

            SliderControl.ValueChanged += OnSliderValueChanged;
        }

        // ─── Internal logic ───────────────────────────────────────────────────────

        private void OnSliderValueChanged(object? sender, ValueChangedEventArgs e)
        {
            _updatingFromSlider = true;
            Value = e.NewValue;
            _updatingFromSlider = false;
            RefreshValueLabel();
        }

        private void RefreshValueLabel()
        {
            string valueStr = DecimalPlaces > 0
                ? Math.Round(Value, DecimalPlaces).ToString($"F{DecimalPlaces}")
                : ((int)Math.Round(Value)).ToString();
            ValueLabel.Text = $"{valueStr}{Unit}";
        }
    }
}
