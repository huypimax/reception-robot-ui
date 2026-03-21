using System.Windows.Input;

namespace RobotHri.Controls
{
    /// <summary>
    /// Collapsible navigation rail that sits on the left edge of a page.
    /// Collapsed (default): NavRailCollapsedWidth — icons only.
    /// Expanded: NavRailExpandedWidth — icons + labels, toggled by the ☰ "Main" button.
    /// </summary>
    public partial class NavRail : ContentView
    {
        // ─── Command BindableProperties ───────────────────────────────────────────

        public static readonly BindableProperty QnaCommandProperty =
            BindableProperty.Create(nameof(QnaCommand), typeof(ICommand), typeof(NavRail));

        public static readonly BindableProperty NaviCommandProperty =
            BindableProperty.Create(nameof(NaviCommand), typeof(ICommand), typeof(NavRail));

        public static readonly BindableProperty LabCommandProperty =
            BindableProperty.Create(nameof(LabCommand), typeof(ICommand), typeof(NavRail));

        public static readonly BindableProperty DeliCommandProperty =
            BindableProperty.Create(nameof(DeliCommand), typeof(ICommand), typeof(NavRail));

        public static readonly BindableProperty CheckinCommandProperty =
            BindableProperty.Create(nameof(CheckinCommand), typeof(ICommand), typeof(NavRail));

        // ─── Label BindableProperties ─────────────────────────────────────────────

        public static readonly BindableProperty MainLabelProperty =
            BindableProperty.Create(nameof(MainLabel), typeof(string), typeof(NavRail), "Main",
                propertyChanged: (b, _, n) => ((NavRail)b).MainText.Text = (string)n);

        public static readonly BindableProperty QnaLabelProperty =
            BindableProperty.Create(nameof(QnaLabel), typeof(string), typeof(NavRail), "Q&A",
                propertyChanged: (b, _, n) => ((NavRail)b).QnaText.Text = (string)n);

        public static readonly BindableProperty NaviLabelProperty =
            BindableProperty.Create(nameof(NaviLabel), typeof(string), typeof(NavRail), "Navigation",
                propertyChanged: (b, _, n) => ((NavRail)b).NaviText.Text = (string)n);

        public static readonly BindableProperty LabLabelProperty =
            BindableProperty.Create(nameof(LabLabel), typeof(string), typeof(NavRail), "Lab",
                propertyChanged: (b, _, n) => ((NavRail)b).LabText.Text = (string)n);

        public static readonly BindableProperty DeliLabelProperty =
            BindableProperty.Create(nameof(DeliLabel), typeof(string), typeof(NavRail), "Delivery",
                propertyChanged: (b, _, n) => ((NavRail)b).DeliText.Text = (string)n);

        public static readonly BindableProperty CheckinLabelProperty =
            BindableProperty.Create(nameof(CheckinLabel), typeof(string), typeof(NavRail), "Check-in",
                propertyChanged: (b, _, n) => ((NavRail)b).CheckinText.Text = (string)n);

        // ─── CLR wrappers ─────────────────────────────────────────────────────────

        public ICommand? QnaCommand     { get => (ICommand?)GetValue(QnaCommandProperty);     set => SetValue(QnaCommandProperty, value); }
        public ICommand? NaviCommand    { get => (ICommand?)GetValue(NaviCommandProperty);    set => SetValue(NaviCommandProperty, value); }
        public ICommand? LabCommand     { get => (ICommand?)GetValue(LabCommandProperty);     set => SetValue(LabCommandProperty, value); }
        public ICommand? DeliCommand    { get => (ICommand?)GetValue(DeliCommandProperty);    set => SetValue(DeliCommandProperty, value); }
        public ICommand? CheckinCommand { get => (ICommand?)GetValue(CheckinCommandProperty); set => SetValue(CheckinCommandProperty, value); }

        public string MainLabel    { get => (string)GetValue(MainLabelProperty);    set => SetValue(MainLabelProperty, value); }
        public string QnaLabel     { get => (string)GetValue(QnaLabelProperty);     set => SetValue(QnaLabelProperty, value); }
        public string NaviLabel    { get => (string)GetValue(NaviLabelProperty);    set => SetValue(NaviLabelProperty, value); }
        public string LabLabel     { get => (string)GetValue(LabLabelProperty);     set => SetValue(LabLabelProperty, value); }
        public string DeliLabel    { get => (string)GetValue(DeliLabelProperty);    set => SetValue(DeliLabelProperty, value); }
        public string CheckinLabel { get => (string)GetValue(CheckinLabelProperty); set => SetValue(CheckinLabelProperty, value); }

        // ─── State ────────────────────────────────────────────────────────────────

        private bool _isExpanded;
        private bool _isAnimating;

        // Read animation widths from the shared resource dictionary so they stay
        // in sync with NavRailCollapsedWidth / NavRailExpandedWidth in Dimens.xaml.
        private double CollapsedWidth =>
            Application.Current?.Resources.TryGetValue("NavRailCollapsedWidth", out var v) == true
                ? (double)v : 72;

        private double ExpandedWidth =>
            Application.Current?.Resources.TryGetValue("NavRailExpandedWidth", out var v) == true
                ? (double)v : 200;

        // ─── Constructor ──────────────────────────────────────────────────────────

        public NavRail()
        {
            InitializeComponent();

            // Sync all label texts to their BindableProperty defaults immediately
            // (same pattern as HeaderLayout — callbacks only fire on value change).
            MainText.Text    = MainLabel;
            QnaText.Text     = QnaLabel;
            NaviText.Text    = NaviLabel;
            LabText.Text     = LabLabel;
            DeliText.Text    = DeliLabel;
            CheckinText.Text = CheckinLabel;

            MenuTap.Tapped    += OnMenuTapped;
            QnaTap.Tapped     += (_, _) => QnaCommand?.Execute(null);
            NaviTap.Tapped    += (_, _) => NaviCommand?.Execute(null);
            LabTap.Tapped     += (_, _) => LabCommand?.Execute(null);
            DeliTap.Tapped    += (_, _) => DeliCommand?.Execute(null);
            CheckinTap.Tapped += (_, _) => CheckinCommand?.Execute(null);
        }

        // ─── Toggle logic ─────────────────────────────────────────────────────────

        private async void OnMenuTapped(object? sender, TappedEventArgs e)
        {
            if (_isAnimating) return;
            _isAnimating = true;
            _isExpanded  = !_isExpanded;

            if (_isExpanded)
            {
                await AnimateWidth(CollapsedWidth, ExpandedWidth);
                SetLabelsVisible(true);
            }
            else
            {
                SetLabelsVisible(false);
                await AnimateWidth(ExpandedWidth, CollapsedWidth);
            }

            _isAnimating = false;
        }

        private Task AnimateWidth(double from, double to)
        {
            var tcs       = new TaskCompletionSource();
            var animation = new Animation(v => RailContainer.WidthRequest = v, from, to);
            animation.Commit(this, "RailWidth", length: 250, easing: Easing.CubicInOut,
                finished: (_, _) => tcs.TrySetResult());
            return tcs.Task;
        }

        private void SetLabelsVisible(bool visible)
        {
            MainText.IsVisible    = visible;
            QnaText.IsVisible     = visible;
            NaviText.IsVisible    = visible;
            LabText.IsVisible     = visible;
            DeliText.IsVisible    = visible;
            CheckinText.IsVisible = visible;
        }
    }
}
