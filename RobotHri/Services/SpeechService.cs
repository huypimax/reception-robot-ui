using CommunityToolkit.Maui.Media;
using RobotHri.Constants;

namespace RobotHri.Services
{
    /// <summary>
    /// Speech service using MAUI built-in TextToSpeech and CommunityToolkit SpeechToText.
    /// Mirrors thread_speak.py (TTS) and thread_listen.py (STT).
    /// </summary>
    public class SpeechService : ISpeechService
    {
        public const string ListenErrorPermissionDenied = "__LISTEN_ERROR_PERMISSION_DENIED__";
        public const string ListenErrorServiceUnavailable = "__LISTEN_ERROR_SERVICE_UNAVAILABLE__";
        private readonly ISpeechToText _speechToText;
        private CancellationTokenSource? _ttsCts;
        private CancellationTokenSource? _sttCts;

        public bool IsSpeaking { get; private set; }
        public bool IsListening { get; private set; }

        public event EventHandler<string>? SpeechRecognized;
        public event EventHandler? SpeakingStarted;
        public event EventHandler? SpeakingCompleted;

        public SpeechService(ISpeechToText speechToText)
        {
            _speechToText = speechToText;
        }

        public async Task SpeakAsync(string text, string languageCode = "vi")
        {
            await StopSpeakingAsync();
            _ttsCts = new CancellationTokenSource();

            try
            {
                IsSpeaking = true;
                SpeakingStarted?.Invoke(this, EventArgs.Empty);

                var settings = new SpeechOptions
                {
                    Locale = await GetLocaleAsync(languageCode),
                };

                await TextToSpeech.Default.SpeakAsync(text, settings, _ttsCts.Token);
            }
            catch (OperationCanceledException) { }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[TTS] Error: {ex.Message}");
            }
            finally
            {
                IsSpeaking = false;
                SpeakingCompleted?.Invoke(this, EventArgs.Empty);
            }
        }

        public async Task StopSpeakingAsync()
        {
            _ttsCts?.Cancel();
            _ttsCts = null;
            IsSpeaking = false;
            await Task.CompletedTask;
        }

        public async Task<string?> ListenAsync(string languageCode = "vi",
            CancellationToken cancellationToken = default)
        {
            _sttCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);

            try
            {
                IsListening = true;

                var isGranted = await _speechToText.RequestPermissions(_sttCts.Token);
                if (!isGranted) return ListenErrorPermissionDenied;

                var localeCode = AppConstants.SpeechLanguages.TryGetValue(languageCode, out var lc)
                    ? lc : "vi-VN";

                var tcs = new TaskCompletionSource<string?>();
                string? partialText = null;

                void OnResultCompleted(object? sender, SpeechToTextRecognitionResultCompletedEventArgs e)
                {
                    _speechToText.RecognitionResultCompleted -= OnResultCompleted;
                    _speechToText.RecognitionResultUpdated -= OnResultUpdated;
                    if (e.RecognitionResult.IsSuccessful)
                    {
                        SpeechRecognized?.Invoke(this, e.RecognitionResult.Text);
                        tcs.TrySetResult(e.RecognitionResult.Text);
                    }
                    else
                    {
                        tcs.TrySetResult(partialText);
                    }
                }

                void OnResultUpdated(object? sender, SpeechToTextRecognitionResultUpdatedEventArgs e)
                {
                    // RecognitionResult is a string for Updated events
                    partialText = e.RecognitionResult;
                    if (!string.IsNullOrWhiteSpace(partialText))
                        SpeechRecognized?.Invoke(this, partialText);
                }

                _speechToText.RecognitionResultCompleted += OnResultCompleted;
                _speechToText.RecognitionResultUpdated += OnResultUpdated;

                var options = new SpeechToTextOptions
                {
                    Culture = new System.Globalization.CultureInfo(localeCode),
                    ShouldReportPartialResults = true,
                };

                await _speechToText.StartListenAsync(options, _sttCts.Token);

                // Wait for completion or cancellation
                using var reg = _sttCts.Token.Register(() =>
                {
                    // remove handlers using the same method groups we attached earlier
                    _speechToText.RecognitionResultCompleted -= OnResultCompleted;
                    _speechToText.RecognitionResultUpdated -= OnResultUpdated;
                    tcs.TrySetCanceled();
                });

                var result = await tcs.Task;
                await _speechToText.StopListenAsync(_sttCts.Token);
                return result;
            }
            catch (OperationCanceledException) { return null; }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[STT] Error: {ex.Message}");
                return ListenErrorServiceUnavailable;
            }
            finally
            {
                try
                {
                    if (_sttCts != null)
                        await _speechToText.StopListenAsync(_sttCts.Token);
                }
                catch { }
                IsListening = false;
            }
        }

        private async Task<Locale?> GetLocaleAsync(string languageCode)
        {
            try
            {
                var locales = await TextToSpeech.Default.GetLocalesAsync();
                var fullCode = AppConstants.SpeechLanguages.TryGetValue(languageCode, out var lc)
                    ? lc : "vi-VN";

                var exact = locales.FirstOrDefault(l =>
                    string.Equals(l.Language, fullCode, StringComparison.OrdinalIgnoreCase));
                if (exact != null) return exact;

                return null;
            }
            catch { return null; }
        }
    }
}
