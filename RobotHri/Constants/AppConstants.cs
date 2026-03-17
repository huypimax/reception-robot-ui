namespace RobotHri.Constants
{
    public static class AppConstants
    {
        public const string AssistantName = "AIko";
        public const string ModelName = "gemini-2.5-pro";
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

        // Language display names used in AI prompts
        public const string LanguageNameVi = "TIẾNG VIỆT";
        public const string LanguageNameEn = "ENGLISH";

        // Navigation destinations (place key → nav key string)
        public static readonly List<(string PlaceKey, string ButtonId)> PlaceButtonPairs = new()
        {
            ("Water Intake", "btn_room_a"),
            ("Chemistry Hall", "btn_room_b"),
            ("Restroom", "btn_room_c"),
            ("Stairs", "btn_room_d"),
            ("Robotics Lab", "btn_room_e"),
            ("Electrical Lab", "btn_room_f"),
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
