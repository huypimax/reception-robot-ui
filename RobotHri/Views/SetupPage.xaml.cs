using Microsoft.Maui.Devices;
using RobotHri.Controls.Base;
using RobotHri.ViewModels;

namespace RobotHri.Views
{
    public partial class SetupPage : BaseContentPage
    {
        private readonly SetupViewModel _viewModel;

        public SetupPage(SetupViewModel viewModel)
        {
            InitializeComponent();
            _viewModel = viewModel;
            BindingContext = viewModel;
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
            SizeChanged += (_, _) => UpdateRobotMapHostHeight();
        }

        private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(SetupViewModel.IsMapSelected))
                Dispatcher.Dispatch(UpdateRobotMapHostHeight);
        }

        /// <summary>
        /// Sizes the map card to most of the window so the occupancy grid can fill the screen (still inside scroll).
        /// </summary>
        private void UpdateRobotMapHostHeight()
        {
            if (!IsLoaded || RobotMapHost is null)
                return;
            if (!_viewModel.IsMapSelected)
                return;

            var winH = Window?.Height ?? Height;
            if (winH <= 0)
            {
                var di = DeviceDisplay.Current.MainDisplayInfo;
                winH = di.Height / di.Density;
            }

            // Space for map title, pose line, hint, padding, and shell / status chrome.
            const double reserved = 220;
            var mapH = Math.Clamp(winH - reserved, 320, 1600);
            RobotMapHost.HeightRequest = mapH;
        }

        protected override void OnAppearing()
        {
            base.OnAppearing();
            _ = _viewModel.ReloadFromStoreAsync();
            _viewModel.AttachMqttHandlers();
            Dispatcher.Dispatch(UpdateRobotMapHostHeight);
        }

        protected override void OnDisappearing()
        {
            _viewModel.DetachMqttHandlers();
            base.OnDisappearing();
        }

        protected override void RefreshLocalizedText()
        {
            // All labels are bound via INotifyPropertyChanged on the ViewModel.
        }
    }
}
