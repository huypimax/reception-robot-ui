namespace RobotHri.Constants
{
    public static class AppConstants
    {
        public const string AssistantName = "AIko";
        public const string ModelName = "gemini-2.0-flash";
        public const string DefaultLanguage = "vi";

        // TTS voice codes per language
        public static readonly Dictionary<string, string> TtsVoices = new()
        {
            { "vi", "vi-VN-HoaiMyNeural" },
            { "en", "en-US-GuyNeural" }
        };

        // Speech recognition language codes
        public static readonly Dictionary<string, string> SpeechLanguages = new()
        {
            { "vi", "vi-VN" },
            { "en", "en-US" }
        };
       
        // Offline response keyword triggers
        public static readonly string[] KeywordsGoodbye =
            { "stop", "bye", "thank you", "tạm biệt", "cảm ơn", "dừng" };
        public static readonly string[] KeywordsTime =
            { "time", "giờ", "mấy giờ" };
        public static readonly string[] KeywordsDate =
            { "what day", "what date", "ngày", "hôm nay" };
        public static readonly string[] KeywordsRepeat =
            { "repeat", "say it again", "lặp lại", "nói lại" };
    }
}
