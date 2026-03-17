namespace RobotHri.Controls
{
    /// <summary>
    /// Room navigation button with press animation.
    /// Mirrors btn_room_a..f in the original Qt UI.
    /// </summary>
    public partial class NavRoomButton : ContentView
    {
        public static readonly BindableProperty RoomNameProperty =
            BindableProperty.Create(nameof(RoomName), typeof(string), typeof(NavRoomButton), string.Empty,
                propertyChanged: (b, o, n) => ((NavRoomButton)b).RoomLabel.Text = (string)n);

        public static readonly BindableProperty RoomKeyProperty =
            BindableProperty.Create(nameof(RoomKey), typeof(string), typeof(NavRoomButton), string.Empty);

        public static readonly BindableProperty IconSourceProperty =
            BindableProperty.Create(nameof(IconSource), typeof(string), typeof(NavRoomButton), null,
                propertyChanged: (b, o, n) => ((NavRoomButton)b).UpdateIcon((string?)n));

        public static readonly BindableProperty IsActiveProperty =
            BindableProperty.Create(nameof(IsActive), typeof(bool), typeof(NavRoomButton), false,
                propertyChanged: (b, o, n) => ((NavRoomButton)b).UpdateActiveState((bool)n));

        public string RoomName
        {
            get => (string)GetValue(RoomNameProperty);
            set => SetValue(RoomNameProperty, value);
        }

        public string RoomKey
        {
            get => (string)GetValue(RoomKeyProperty);
            set => SetValue(RoomKeyProperty, value);
        }

        public string? IconSource
        {
            get => (string?)GetValue(IconSourceProperty);
            set => SetValue(IconSourceProperty, value);
        }

        public bool IsActive
        {
            get => (bool)GetValue(IsActiveProperty);
            set => SetValue(IsActiveProperty, value);
        }

        public event EventHandler<string>? RoomSelected;

        public NavRoomButton()
        {
            InitializeComponent();
            RoomTap.Tapped += OnRoomTapped;
        }

        private async void OnRoomTapped(object? sender, TappedEventArgs e)
        {
            await RoomBorder.ScaleTo(0.94, 80);
            await RoomBorder.ScaleTo(1.0, 80);
            RoomSelected?.Invoke(this, RoomKey);
        }

        private void UpdateIcon(string? source)
        {
            RoomIcon.IsVisible = !string.IsNullOrEmpty(source);
            if (!string.IsNullOrEmpty(source))
                RoomIcon.Source = source;
        }

        private void UpdateActiveState(bool active)
        {
            RoomBorder.BackgroundColor = active
                ? Color.FromArgb("#00294D")
                : Colors.White;
            RoomLabel.TextColor = active
                ? Colors.White
                : Color.FromArgb("#00294D");
        }
    }
}
