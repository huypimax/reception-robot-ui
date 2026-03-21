using RobotHri.Controls.Base;
using RobotHri.ViewModels;

namespace RobotHri.Views
{
    public partial class SetupPage : BaseContentPage
    {
        public SetupPage(SetupViewModel viewModel)
        {
            InitializeComponent();
            BindingContext = viewModel;
        }

        protected override void RefreshLocalizedText()
        {
            // All labels are bound via INotifyPropertyChanged on the ViewModel.
        }
    }
}
