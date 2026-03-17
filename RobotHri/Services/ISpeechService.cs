namespace RobotHri.Services
{
    public interface ISpeechService
    {
        bool IsSpeaking { get; }
        bool IsListening { get; }

        Task SpeakAsync(string text, string languageCode = "vi");
        Task StopSpeakingAsync();
        Task<string?> ListenAsync(string languageCode = "vi", CancellationToken cancellationToken = default);

        event EventHandler<string> SpeechRecognized;
        event EventHandler SpeakingStarted;
        event EventHandler SpeakingCompleted;
    }
}
