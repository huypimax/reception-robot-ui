using Moq;
using NUnit.Framework;
using RobotHri.Languages;
using RobotHri.Services;
using RobotHri.ViewModels;
using System.Threading.Tasks;
using System;

namespace RobotHri.Tests
{
    [TestFixture]
    public class NaviViewModelTests
    {
        private Mock<ILocalizationService> _mockLocalizationService;
        private Mock<IMqttService> _mockMqttService;
        private Mock<ISpeechService> _mockSpeechService;
        private NaviViewModel _viewModel;

        [SetUp]
        public void Setup()
        {
            _mockLocalizationService = new Mock<ILocalizationService>();
            _mockMqttService = new Mock<IMqttService>();
            _mockSpeechService = new Mock<ISpeechService>();

            // Setup basic localization mocking to avoid null reference exceptions if StringIds are used.
            // Since StringIds is a static class returning strings, we might not need to mock it directly here,
            // but we mock the localization service methods just in case.
            _mockLocalizationService.Setup(l => l.GetCurrentLanguageName()).Returns("EN");
            _mockLocalizationService.Setup(l => l.CurrentLanguageCode).Returns("en-US");

            _mockMqttService.Setup(m => m.IsConnected).Returns(true);

            _viewModel = new NaviViewModel(
                _mockLocalizationService.Object,
                _mockMqttService.Object,
                _mockSpeechService.Object);
        }

        [Test]
        public void OnRoomSelected_StartsNavigation_SetsIsBusyAndLoadingMessage()
        {
            // Arrange
            string testRoomKey = "RoomWaterIntake";
            string expectedRoomName = StringIds.NAV_ROOM_WATER_INTAKE.GetString();
            string expectedHeadingMessage = StringIds.NAV_HEADING_TO.GetString().Format(("place", expectedRoomName));

            // Act
            _viewModel.SelectRoomCommand.Execute(testRoomKey);

            // Assert
            Assert.That(_viewModel.IsBusy, Is.True);
            Assert.That(_viewModel.ActiveRoomKey, Is.EqualTo(testRoomKey));
            Assert.That(_viewModel.LoadingMessage, Is.EqualTo(expectedHeadingMessage));
            Assert.That(_viewModel.PromptText, Is.EqualTo(expectedHeadingMessage));

            _mockSpeechService.Verify(s => s.SpeakAsync(expectedHeadingMessage, "en-US"), Times.Once);
            _mockMqttService.Verify(m => m.PublishGoalAsync("Water Intake"), Times.Once);
        }

        [Test]
        public async Task OnRoomSelected_WhenNotConnectedAndConnectFails_ResetsStateAndDoesNotPublish()
        {
            _mockMqttService.Setup(m => m.IsConnected).Returns(false);
            _mockMqttService.Setup(m => m.ConnectAsync()).ReturnsAsync(false);
            _mockSpeechService.Setup(s => s.SpeakAsync(It.IsAny<string>(), It.IsAny<string>()))
                .Returns(Task.CompletedTask);

            var viewModel = new NaviViewModel(
                _mockLocalizationService.Object,
                _mockMqttService.Object,
                _mockSpeechService.Object);

            viewModel.SelectRoomCommand.Execute("btn_room_a");
            await Task.Delay(300);

            Assert.That(viewModel.IsBusy, Is.False);
            Assert.That(viewModel.ActiveRoomKey, Is.Null);
            Assert.That(viewModel.LoadingMessage, Is.Empty);
            Assert.That(viewModel.PromptText, Is.EqualTo(StringIds.NAV_WHERE_TO_GO.GetString()));

            _mockMqttService.Verify(m => m.ConnectAsync(), Times.Once);
            _mockMqttService.Verify(m => m.PublishGoalAsync(It.IsAny<string>()), Times.Never);
        }

        [Test]
        public void OnRoomSelected_WhenAlreadyBusy_DoesNotStartNavigationAgain()
        {
            // Arrange
            _viewModel.IsBusy = true;
            string testRoomKey = "RoomChemistryHall";

            // Act
            _viewModel.SelectRoomCommand.Execute(testRoomKey);

            // Assert
            Assert.That(_viewModel.ActiveRoomKey, Is.Null); // Should not have changed
            _mockSpeechService.Verify(s => s.SpeakAsync(It.IsAny<string>(), It.IsAny<string>()), Times.Never);
            _mockMqttService.Verify(m => m.PublishGoalAsync(It.IsAny<string>()), Times.Never);
        }

        [Test]
        public void OnCancelNavigation_WhenBusy_ClearsStateAndStopsSpeech()
        {
            // Arrange
            _viewModel.IsBusy = true;
            _viewModel.ActiveRoomKey = "RoomWaterIntake";
            _viewModel.LoadingMessage = "Heading somewhere";

            // Act
            _viewModel.CancelNavigationCommand.Execute(null);

            // Assert
            Assert.That(_viewModel.IsBusy, Is.False);
            Assert.That(_viewModel.ActiveRoomKey, Is.Null);
            Assert.That(_viewModel.LoadingMessage, Is.Empty);
            Assert.That(_viewModel.PromptText, Is.EqualTo(StringIds.NAV_WHERE_TO_GO.GetString()));

            _mockSpeechService.Verify(s => s.StopSpeakingAsync(), Times.Once);
        }

        [Test]
        public void OnArrivalReceived_WhenArrivedIsTrue_ClearsStateAndSpeaks()
        {
            // Arrange
            string testRoomKey = "RoomRestroom";
            _viewModel.IsBusy = true;
            _viewModel.ActiveRoomKey = testRoomKey;

            string expectedRoomName = StringIds.NAV_ROOM_RESTROOM.GetString();
            string expectedArrivedMessage = StringIds.NAV_ARRIVED_READY.GetString().Format(("place", expectedRoomName));

            // Act
            // We need to trigger the event on the mocked service
            _mockMqttService.Raise(m => m.ArrivalReceived += null, this, true);

            // Assert
            Assert.That(_viewModel.IsBusy, Is.False);
            Assert.That(_viewModel.ActiveRoomKey, Is.Null);
            Assert.That(_viewModel.LoadingMessage, Is.Empty);
            Assert.That(_viewModel.PromptText, Is.EqualTo(expectedArrivedMessage));

            _mockSpeechService.Verify(s => s.SpeakAsync(expectedArrivedMessage, "en-US"), Times.Once);

            // Note: Testing the DisplayAlert popup is tricky in a unit test context because it relies on Application.Current.
            // Ideally, the popup logic should be abstracted into a UI/Dialog service that can be mocked.
            // Since it's not, we skip asserting the DisplayAlert here to avoid test failure due to Application.Current being null.
        }

        [Test]
        public void OnArrivalReceived_WhenArrivedIsFalse_DoesNothing()
        {
            // Arrange
            _viewModel.IsBusy = true;
            _viewModel.ActiveRoomKey = "RoomWaterIntake";

            // Act
            _mockMqttService.Raise(m => m.ArrivalReceived += null, this, false);

            // Assert
            Assert.That(_viewModel.IsBusy, Is.True); // Should still be busy
            Assert.That(_viewModel.ActiveRoomKey, Is.Not.Null); // Key should remain
        }
    }
}
