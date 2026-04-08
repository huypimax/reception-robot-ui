using Moq;
using NUnit.Framework;
using RobotHri.Languages;
using RobotHri.Services;
using RobotHri.ViewModels;

namespace RobotHri.Tests
{
    [TestFixture]
    public class QnaViewModelTests
    {
        private Mock<ILocalizationService> _mockLocalizationService = null!;
        private Mock<ISpeechService> _mockSpeechService = null!;
        private Mock<IQnaResponseService> _mockQnaResponseService = null!;
        private QnaViewModel _viewModel = null!;

        [SetUp]
        public void Setup()
        {
            _mockLocalizationService = new Mock<ILocalizationService>();
            _mockSpeechService = new Mock<ISpeechService>();
            _mockQnaResponseService = new Mock<IQnaResponseService>();

            _mockLocalizationService.Setup(l => l.GetCurrentLanguageName()).Returns("EN");
            _mockLocalizationService.Setup(l => l.CurrentLanguageCode).Returns("en");

            _viewModel = new QnaViewModel(
                _mockLocalizationService.Object,
                _mockSpeechService.Object,
                _mockQnaResponseService.Object);
        }

        [Test]
        public async Task ToggleMic_WhenTranscriptAndAnswerAvailable_SetsPromptToAnswerAndSpeaks()
        {
            _mockSpeechService
                .Setup(s => s.ListenAsync("en", It.IsAny<CancellationToken>()))
                .ReturnsAsync("where is fablab");

            _mockQnaResponseService
                .Setup(s => s.GetAnswerAsync("where is fablab", "en", It.IsAny<CancellationToken>()))
                .ReturnsAsync("Fablab is at HCMUT campus.");

            _mockSpeechService
                .Setup(s => s.SpeakAsync("Fablab is at HCMUT campus.", "en"))
                .Returns(Task.CompletedTask);

            _viewModel.ToggleMicCommand.Execute(null);
            await WaitForAsync(() => _viewModel.PromptText == "Fablab is at HCMUT campus.");

            Assert.That(_viewModel.IsListening, Is.False);
            Assert.That(_viewModel.IsMicActive, Is.False);
            Assert.That(_viewModel.PromptText, Is.EqualTo("Fablab is at HCMUT campus."));
            _mockQnaResponseService.Verify(
                s => s.GetAnswerAsync("where is fablab", "en", It.IsAny<CancellationToken>()),
                Times.Once);
            _mockSpeechService.Verify(
                s => s.SpeakAsync("Fablab is at HCMUT campus.", "en"),
                Times.Once);
        }

        [Test]
        public async Task ToggleMic_WhenListenReturnsEmpty_ShowsListeningErrorAndSkipsQna()
        {
            _mockSpeechService
                .Setup(s => s.ListenAsync("en", It.IsAny<CancellationToken>()))
                .ReturnsAsync((string?)null);

            _viewModel.ToggleMicCommand.Execute(null);
            await WaitForAsync(() => _viewModel.IsListening == false);

            Assert.That(_viewModel.PromptText, Is.EqualTo(StringIds.ERROR_LISTENING.GetString()));
            _mockQnaResponseService.Verify(
                s => s.GetAnswerAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()),
                Times.Never);
        }

        [Test]
        public async Task ToggleMic_WhenListenServiceUnavailable_ShowsSpeechUnavailableError()
        {
            _mockSpeechService
                .Setup(s => s.ListenAsync("en", It.IsAny<CancellationToken>()))
                .ReturnsAsync(SpeechService.ListenErrorServiceUnavailable);

            _viewModel.ToggleMicCommand.Execute(null);
            await WaitForAsync(() => _viewModel.IsListening == false);

            Assert.That(_viewModel.PromptText, Is.EqualTo(StringIds.ERROR_SPEECH_UNAVAILABLE.GetString()));
            _mockQnaResponseService.Verify(
                s => s.GetAnswerAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()),
                Times.Never);
        }

        private static async Task WaitForAsync(Func<bool> condition, int timeoutMs = 2000)
        {
            var start = DateTime.UtcNow;
            while (!condition())
            {
                if ((DateTime.UtcNow - start).TotalMilliseconds > timeoutMs)
                    Assert.Fail("Timed out waiting for async condition.");
                await Task.Delay(25);
            }
        }
    }
}
