namespace RobotHri.Languages
{
    /// <summary>
    /// All string key constants for localization. Mirrors src/utilities/string_ids.py.
    /// Usage: StringIds.APP_NAME.GetString()
    /// </summary>
    public static class StringIds
    {
        // ==================== App & Welcome ====================
        public const string APP_NAME = "app_name";
        public const string APP_WELCOME = "app_welcome";
        public const string WELCOME_GOOD_MORNING = "welcome_good_morning";
        public const string WELCOME_GOOD_AFTERNOON = "welcome_good_afternoon";
        public const string WELCOME_GOOD_EVENING = "welcome_good_evening";
        public const string WELCOME_GREETING = "welcome_greeting";

        // ==================== Main Page ====================
        public const string MAIN_TITLE = "main_title";
        public const string MAIN_QNA = "main_qna";
        public const string MAIN_NAVIGATION = "main_navigation";
        public const string MAIN_LAB = "main_lab";
        public const string MAIN_DELIVERY = "main_delivery";
        public const string MAIN_CHECKIN = "main_checkin";

        // ==================== Q&A Page ====================
        public const string QNA_TITLE = "qna_title";
        public const string QNA_LISTENING = "qna_listening";
        public const string QNA_FINDING_ANSWER = "qna_finding_answer";
        public const string QNA_TAP_MICROPHONE = "qna_tap_microphone";
        public const string QNA_HOME = "qna_home";

        // ==================== Navigation Page ====================
        public const string NAV_TITLE = "nav_title";
        public const string NAV_WHERE_TO_GO = "nav_where_to_go";
        public const string NAV_WHERE_TO_GO_QUESTION = "nav_where_to_go_question";
        public const string NAV_HEADING_TO = "nav_heading_to";
        public const string NAV_ALREADY_HERE = "nav_already_here";
        public const string NAV_LETS_MOVE = "nav_lets_move";
        public const string NAV_ARRIVED_AT = "nav_arrived_at";
        public const string NAV_ARRIVED_READY = "nav_arrived_ready";
        public const string NAV_HOME = "nav_home";
        public const string NAV_ROOM_WATER_INTAKE = "nav_room_water_intake";
        public const string NAV_ROOM_CHEMISTRY_HALL = "nav_room_chemistry_hall";
        public const string NAV_ROOM_RESTROOM = "nav_room_restroom";
        public const string NAV_ROOM_STAIRS = "nav_room_stairs";
        public const string NAV_ROOM_ROBOTICS_LAB = "nav_room_robotics_lab";
        public const string NAV_ROOM_ELECTRICAL_LAB = "nav_room_electrical_lab";

        // ==================== Lab Page ====================
        public const string LAB_TITLE = "lab_title";
        public const string LAB_HOME = "lab_home";
        public const string LAB_BACK = "lab_back";
        public const string LAB_PROMPT = "lab_prompt";
        public const string LAB_SYSTEM_DIAGRAM = "lab_system_diagram";
        public const string LAB_ABOUT_IFM = "lab_about_ifm";
        public const string LAB_ABOUT_PLC = "lab_about_plc";
        public const string LAB_ABOUT_STEP = "lab_about_step";
        public const string LAB_ABOUT_HMI = "lab_about_hmi";
        public const string LAB_READ_ALOUD = "lab_read_aloud";
        public const string LAB_DEVICE_IFM = "lab_device_ifm";
        public const string LAB_DEVICE_STEP = "lab_device_step";
        public const string LAB_DEVICE_PLC = "lab_device_plc";
        public const string LAB_DEVICE_HMI = "lab_device_hmi";

        // ==================== Delivery Page ====================
        public const string DELI_TITLE = "deli_title";
        public const string DELI_HOME = "deli_home";
        public const string DELI_FORM_TITLE = "deli_form_title";
        public const string DELI_DESTINATION = "deli_destination";
        public const string DELI_ITEM_LABEL = "deli_item_label";
        public const string DELI_RECEIVER_LABEL = "deli_receiver_label";
        public const string DELI_SENDER_LABEL = "deli_sender_label";
        public const string DELI_NOTE_LABEL = "deli_note_label";
        public const string DELI_CHOOSE_DESTINATION = "deli_choose_destination";
        public const string DELI_DELIVERING_NOW = "deli_delivering_now";
        public const string DELI_ITEM_ARRIVED = "deli_item_arrived";
        public const string DELI_GET_READY = "deli_get_ready";
        public const string DELI_START_DELIVERY = "deli_start_delivery";
        public const string DELI_RECEIVED = "deli_received";

        // ==================== Common ====================
        public const string COMMON_HOME = "common_home";
        public const string COMMON_BACK = "common_back";
        public const string COMMON_ERROR = "common_error";
        public const string COMMON_LOADING = "common_loading";
        public const string COMMON_LANGUAGE = "common_language";
        public const string COMMON_SWITCH_LANGUAGE = "common_switch_language";

        // ==================== Error Messages ====================
        public const string ERROR_LISTENING = "error_listening";
        public const string ERROR_SPEECH_UNAVAILABLE = "error_speech_unavailable";
        public const string ERROR_STILL_THERE = "error_still_there";
        public const string ERROR_SOMETHING_WRONG = "error_something_wrong";
        public const string ERROR_TTS = "error_tts";
        public const string ERROR_API = "error_api";

        // ==================== AI Offline Responses ====================
        public const string AI_OFFLINE_GOODBYE = "ai_offline_goodbye";
        public const string AI_OFFLINE_TIME = "ai_offline_time";
        public const string AI_OFFLINE_DATE = "ai_offline_date";
        public const string AI_OFFLINE_REPEAT = "ai_offline_repeat";

        // ==================== AI FAQ Responses ====================
        public const string AI_FAQ_HCMUT = "ai_faq_hcmut";
        public const string AI_FAQ_IVS = "ai_faq_ivs";
        public const string AI_FAQ_FABLAB = "ai_faq_fablab";
        public const string AI_FAQ_MEMBERS = "ai_faq_members";
        public const string AI_FAQ_CREATOR = "ai_faq_creator";
        public const string AI_FAQ_NAME = "ai_faq_name";
        public const string AI_FAQ_HELP = "ai_faq_help";

        // ==================== AI System & Errors ====================
        public const string AI_SYSTEM_PROMPT = "ai_system_prompt";
        public const string AI_ERROR_RESPONSE = "ai_error_response";
        public const string AI_ERROR_PROCESSING = "ai_error_processing";
        public const string AI_QUERY_NOTE = "ai_query_note";

        // ==================== AI Weather ====================
        public const string AI_WEATHER_CURRENT = "ai_weather_current";
        public const string AI_WEATHER_NOT_FOUND = "ai_weather_not_found";
        public const string AI_WEATHER_ERROR = "ai_weather_error";
        public const string AI_WEATHER_EXCEPTION = "ai_weather_exception";

        // ==================== AI Web Search ====================
        public const string AI_WEB_SEARCH_NO_INFO = "ai_web_search_no_info";
        public const string AI_WEB_SEARCH_ERROR = "ai_web_search_error";

        // ==================== AI Days ====================
        public const string AI_DAYS_MONDAY = "ai_days_monday";
        public const string AI_DAYS_TUESDAY = "ai_days_tuesday";
        public const string AI_DAYS_WEDNESDAY = "ai_days_wednesday";
        public const string AI_DAYS_THURSDAY = "ai_days_thursday";
        public const string AI_DAYS_FRIDAY = "ai_days_friday";
        public const string AI_DAYS_SATURDAY = "ai_days_saturday";
        public const string AI_DAYS_SUNDAY = "ai_days_sunday";

        // ==================== AI Months ====================
        public const string AI_MONTHS_JANUARY = "ai_months_january";
        public const string AI_MONTHS_FEBRUARY = "ai_months_february";
        public const string AI_MONTHS_MARCH = "ai_months_march";
        public const string AI_MONTHS_APRIL = "ai_months_april";
        public const string AI_MONTHS_MAY = "ai_months_may";
        public const string AI_MONTHS_JUNE = "ai_months_june";
        public const string AI_MONTHS_JULY = "ai_months_july";
        public const string AI_MONTHS_AUGUST = "ai_months_august";
        public const string AI_MONTHS_SEPTEMBER = "ai_months_september";
        public const string AI_MONTHS_OCTOBER = "ai_months_october";
        public const string AI_MONTHS_NOVEMBER = "ai_months_november";
        public const string AI_MONTHS_DECEMBER = "ai_months_december";
    }
}
