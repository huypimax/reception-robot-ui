# ==================== Application Constants ====================
ASSISTANT_NAME = "AIko"

# ==================== UI Constants ====================
BTN_LANGUAGE_MIN_SIZE = (100, 50)
BTN_LANGUAGE_MAX_SIZE = (120, 50)

# ==================== Navigation Constants ====================
PLACE_BUTTON_PAIRS = [
    ("Water Intake", "btn_room_a"),
    ("Chemistry Hall", "btn_room_b"),
    ("Restroom", "btn_room_c"),
    ("Stairs", "btn_room_d"),
    ("Robotics Lab", "btn_room_e"),
    ("Electrical Lab", "btn_room_f"),
]

DEFAULT_DESTINATION_PLACEHOLDER = " Choose a destination"

# ==================== Delivery Constants ====================
DIALOG_TITLE_DELIVERY_FAILED = "Delivery Failed"
DIALOG_MSG_NO_DESTINATION = "Oops! You haven't chosen a destination yet"
DIALOG_MSG_NO_SENDER = "Enter the sender, please"
DIALOG_MSG_NO_RECEIVER = "Enter the receiver, please"
DIALOG_MSG_NO_ITEM = "Enter the item, please"

# ==================== Initial Context Templates ====================
INITIAL_CONTEXT_VI = [
    {"role": "user", "parts": [{"text": "Bạn là AIko, một trợ lý ảo thân thiện và ngắn gọn được tạo bởi Fablab. Bạn luôn trả lời bằng tiếng Việt."}]},
    {"role": "model", "parts": [{"text": "Đã hiểu. Tôi là AIko, trợ lý của bạn từ Fablab. Tôi sẽ luôn trả lời bằng tiếng Việt."}]},
    {"role": "user", "parts": [{"text": "Khi trả lời, hãy sử dụng 1-2 câu, dưới 35 từ. Luôn trả lời bằng tiếng Việt."}]},
    {"role": "model", "parts": [{"text": "Đã hiểu. Tôi sẽ giữ câu trả lời ngắn gọn, thân thiện và luôn bằng tiếng Việt."}]},
]

INITIAL_CONTEXT_EN = [
    {"role": "user", "parts": [{"text": "You are AIko, a friendly and concise virtual assistant created by Fablab. You always respond in English."}]},
    {"role": "model", "parts": [{"text": "Understood. I am AIko, your assistant from Fablab. I will always respond in English."}]},
    {"role": "user", "parts": [{"text": "When responding, use 1-2 sentences, under 35 words. Always respond in English."}]},
    {"role": "model", "parts": [{"text": "Understood. I will keep responses brief, friendly and always in English."}]},
]

# ==================== Error Messages ====================
ERROR_BTN_NAME_NONE = "Error: btn_name is None for place '{place}'"

# ==================== Widget IDs ====================
WIDGET_MAIN_CONTAINER = "widget_13"

# ==================== Font Constants ====================
FONT_FAMILY_ROBOTO = "Roboto"
FONT_SIZE_BUTTON = 14

# ==================== AI/Model Constants ====================
MODEL_NAME = "gemini-2.5-pro"

# ==================== Keywords for Offline Responses ====================
KEYWORDS_GOODBYE = ["stop", "bye", "thank you", "tạm biệt", "cảm ơn", "dừng"]
KEYWORDS_TIME = ["time", "giờ", "mấy giờ"]
KEYWORDS_DATE = ["what day", "what date", "ngày", "hôm nay"]
KEYWORDS_REPEAT = ["repeat", "say it again", "lặp lại", "nói lại"]

# ==================== FAQ Keywords ====================
KEYWORDS_HCMUT = [
    "ho chi minh university of technology", "bach khoa", "ho chi minh city university",
    "bach khoa university", "ho chi minh university", "ho chi minh city university of technology",
    "đại học bách khoa", "bách khoa", "hcmut"
]

KEYWORDS_IVS = [
    "ivs", "ivs company", "ivs joint stock company", "individual systems", 
    "ibs company", "công ty ivs"
]

KEYWORDS_FABLAB = [
    "fablab", "innovation lab", "robotics lab", 
    "fab lab", "the lab", "innovation laboratory", "fablab laboratory",
    "phòng lab", "phòng thí nghiệm"
]

KEYWORDS_MEMBERS = [
    "how many people are there in the lab", "how many people work in the lab", 
    "how many members in the lab", "có bao nhiêu người", "bao nhiêu thành viên", 
    "số lượng thành viên"
]

KEYWORDS_CREATOR = [
    "who created you", "your creator", "who made you", "who built you", 
    "who developed you", "who designed you", "who creates you",
    "ai tạo ra bạn", "bạn được tạo bởi", "ai làm ra bạn", "ai phát triển bạn"
]

KEYWORDS_NAME = [
    "what's your name", "what is your name", "your name", "who are you",
    "tên bạn là gì", "bạn tên gì", "bạn là ai"
]

KEYWORDS_HELP = [
    "help", "what can you do", "what are your functions",
    "giúp", "bạn làm được gì", "chức năng của bạn"
]

# ==================== Language Names for System Prompts ====================
LANGUAGE_NAME_VI = "TIẾNG VIỆT"
LANGUAGE_NAME_EN = "ENGLISH"

# ==================== Date/Time Format Constants ====================
TIME_FORMAT = "%H:%M"

# ==================== Speech Recognition Language Codes ====================
# Mapping từ language code của app sang Google Speech Recognition language code
SPEECH_RECOGNITION_LANGUAGES = {
    "vi": "vi-VN",
    "en": "en-US"
}

# ==================== TTS Voice Codes ====================
TTS_VOICES = {
    "vi": "vi-VN-HoaiMyNeural",  # Vietnamese female voice
    "en": "en-US-GuyNeural"  # English male voice (was working before)
}