using RobotHri.Controls.Base;
using RobotHri.ViewModels;

namespace RobotHri.Views
{
    public partial class NaviPage : BaseContentPage
    {
        private readonly NaviViewModel _viewModel;

        public NaviPage(NaviViewModel viewModel)
        {
            InitializeComponent();
            _viewModel = viewModel;
            BindingContext = viewModel;
            Header.BackTapped += (s, e) => viewModel.GoHomeCommand.Execute(null);
            Header.LanguageToggled += (s, e) => viewModel.ToggleLanguageCommand.Execute(null);
        }

        private void OnRoomSelected(object sender, string roomKey)
        {
            _viewModel.SelectRoomCommand.Execute(roomKey);
        }

        protected override void OnDisappearing()
        {
            base.OnDisappearing();
            _ = _viewModel.StopSpeechAsync();
        }
    }
}
