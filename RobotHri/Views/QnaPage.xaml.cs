using RobotHri.Controls.Base;
using RobotHri.ViewModels;

namespace RobotHri.Views
{
    public partial class QnaPage : BaseContentPage
    {
        private readonly QnaViewModel _viewModel;

        public QnaPage(QnaViewModel viewModel)
        {
            InitializeComponent();
            _viewModel = viewModel;
            BindingContext = viewModel;
            Header.BackTapped += (s, e) => viewModel.GoHomeCommand.Execute(null);
            Header.LanguageToggled += (s, e) => viewModel.ToggleLanguageCommand.Execute(null);
        }

        protected override void OnDisappearing()
        {
            base.OnDisappearing();
            _ = _viewModel.StopAllAsync();
        }
    }
}
