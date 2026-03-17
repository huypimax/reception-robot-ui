using RobotHri.Controls.Base;
using RobotHri.ViewModels;

namespace RobotHri.Views
{
    public partial class LabPage : BaseContentPage
    {
        private readonly LabViewModel _viewModel;

        public LabPage(LabViewModel viewModel)
        {
            InitializeComponent();
            _viewModel = viewModel;
            BindingContext = viewModel;
            Header.BackTapped += (s, e) =>
            {
                if (!viewModel.IsDetailVisible)
                    viewModel.GoHomeCommand.Execute(null);
                else
                    viewModel.BackCommand.Execute(null);
            };

            Header.LanguageToggled += (s, e) => viewModel.ToggleLanguageCommand.Execute(null);
        }

        protected override void OnDisappearing()
        {
            base.OnDisappearing();
            // Stop TTS when leaving the page
            _ = _viewModel.StopSpeechAsync();
        }
    }
}
