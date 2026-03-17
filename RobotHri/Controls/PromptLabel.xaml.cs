namespace RobotHri.Controls
{
    /// <summary>
    /// Styled label for displaying status / prompt messages on each page.
    /// Mirrors the prompt_* labels in the original PyQt6 UI.
    /// </summary>
    public partial class PromptLabel : ContentView
    {
        public static readonly BindableProperty TextProperty =
            BindableProperty.Create(nameof(Text), typeof(string), typeof(PromptLabel), string.Empty,
                propertyChanged: (b, o, n) => ((PromptLabel)b).PromptText.Text = (string)n);

        public string Text
        {
            get => (string)GetValue(TextProperty);
            set => SetValue(TextProperty, value);
        }

        public PromptLabel()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Animate text change with a fade transition.
        /// </summary>
        public async Task SetTextAnimatedAsync(string newText)
        {
            await PromptText.FadeTo(0, 150);
            PromptText.Text = newText;
            await PromptText.FadeTo(1, 150);
        }
    }
}
