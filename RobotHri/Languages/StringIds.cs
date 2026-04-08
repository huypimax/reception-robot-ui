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
        // B1 Rooms
        public const string NAV_ROOM_WATER_INTAKE = "nav_room_water_intake";
        public const string NAV_ROOM_CHEMISTRY_HALL = "nav_room_chemistry_hall";
        public const string NAV_ROOM_RESTROOM = "nav_room_restroom";
        public const string NAV_ROOM_STAIRS = "nav_room_stairs";
        public const string NAV_ROOM_ROBOTICS_LAB = "nav_room_robotics_lab";
        public const string NAV_ROOM_ELECTRICAL_LAB = "nav_room_electrical_lab";
        public const string NAV_ROOM_HOME = "nav_room_home";

        // B2 Rooms (Add these to JSON files later if needed, returning defaults for now)
        public const string NAV_ROOM_HOME_2 = "nav_room_home_2";
        public const string NAV_ROOM_LIB = "nav_room_lib";
        public const string NAV_ROOM_VPDOAN = "nav_room_vpdoan";
        public const string NAV_ROOM_BIO_LAB = "nav_room_geo_lab";
        public const string NAV_ROOM_LAB_CEPP = "nav_room_lab_cepp";

        public const string NAV_ARRIVAL_TITLE = "nav_arrival_title";
        public const string NAV_MQTT_CONNECT_FAILED_TITLE = "nav_mqtt_connect_failed_title";
        public const string NAV_MQTT_CONNECT_FAILED_MESSAGE = "nav_mqtt_connect_failed_message";
        public const string NAV_MAP_BUTTON = "nav_map_button";
        public const string NAV_MAP_TITLE = "nav_map_title";
        public const string NAV_MAP_CLOSE = "nav_map_close";
        public const string NAV_MAP_PAN_HINT = "nav_map_pan_hint";
        public const string NAV_MAP_WAITING_POSE = "nav_map_waiting_pose";

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
        public const string OK = "ok";

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

        // ==================== Setup / Settings Page ====================
        public const string SETUP_TITLE                 = "setup_title";
        public const string SETUP_EXIT                  = "setup_exit";
        // Sidebar nav items
        public const string SETUP_NAV_BASIC             = "setup_nav_basic";
        public const string SETUP_NAV_SOUND             = "setup_nav_sound";
        public const string SETUP_NAV_VOICE             = "setup_nav_voice";
        public const string SETUP_NAV_DELIVERY          = "setup_nav_delivery";
        public const string SETUP_NAV_ROUTE             = "setup_nav_route";
        public const string SETUP_NAV_TIME              = "setup_nav_time";
        public const string SETUP_NAV_MAP               = "setup_nav_map";
        public const string SETUP_NAV_EXPRESSION        = "setup_nav_expression";
        public const string SETUP_NAV_SYSTEM            = "setup_nav_system";
        public const string SETUP_NAV_OTHER             = "setup_nav_other";
        public const string SETUP_NAV_UPGRADE           = "setup_nav_upgrade";
        public const string SETUP_NAV_DEVELOPER         = "setup_nav_developer";
        // Route settings panel
        public const string SETUP_ROUTE_WAIT_TIME       = "setup_route_wait_time";
        public const string SETUP_ROUTE_WAIT_TIME_DESC  = "setup_route_wait_time_desc";
        public const string SETUP_ROUTE_SPEED           = "setup_route_speed";
        public const string SETUP_ROUTE_SPEED_DESC      = "setup_route_speed_desc";
        public const string SETUP_ROUTE_MORE            = "setup_route_more";
        // System settings panel
        public const string SETUP_SYS_NETWORK_INFO      = "setup_sys_network_info";
        public const string SETUP_SYS_SSID              = "setup_sys_ssid";
        public const string SETUP_SYS_MAC_HEAD          = "setup_sys_mac_head";
        public const string SETUP_SYS_IP_HEAD           = "setup_sys_ip_head";
        public const string SETUP_SYS_MAC_WLAN          = "setup_sys_mac_wlan";
        public const string SETUP_SYS_IP_WLAN           = "setup_sys_ip_wlan";
        public const string SETUP_SYS_MAC_CHASSIS       = "setup_sys_mac_chassis";
        public const string SETUP_SYS_IMEI              = "setup_sys_imei";
        public const string SETUP_SYS_FACTORY_RESET     = "setup_sys_factory_reset";
        public const string SETUP_SYS_FACTORY_RESET_DESC = "setup_sys_factory_reset_desc";
        public const string SETUP_SYS_FACTORY_RESET_BTN = "setup_sys_factory_reset_btn";
        // Placeholder
        public const string SETUP_COMING_SOON           = "setup_coming_soon";
        // Sound settings
        public const string SETUP_SOUND_TOGGLE         = "setup_sound_toggle";
        public const string SETUP_SOUND_ON             = "setup_sound_on";
        public const string SETUP_SOUND_OFF            = "setup_sound_off";
        public const string SETUP_SOUND_VOLUME         = "setup_sound_volume";
        public const string SETUP_SOUND_MUSIC          = "setup_sound_music";
        public const string SETUP_SOUND_SPEECH         = "setup_sound_speech";
        public const string SETUP_SOUND_OBSTACLE       = "setup_sound_obstacle";
        public const string SETUP_SOUND_CHOOSE_MUSIC   = "setup_sound_choose_music";
        // Basic settings
        public const string SETUP_BASIC_TITLE              = "setup_basic_title";
        public const string SETUP_BASIC_MODE_FAST          = "setup_basic_mode_fast";
        public const string SETUP_BASIC_MODE_MULTI         = "setup_basic_mode_multi";
        public const string SETUP_BASIC_MODE_DIRECT        = "setup_basic_mode_direct";
        public const string SETUP_BASIC_MODE_ROUTE         = "setup_basic_mode_route";
        public const string SETUP_BASIC_MODE_CUSTOM        = "setup_basic_mode_custom";
        public const string SETUP_BASIC_DELIVERY_MODE      = "setup_basic_delivery_mode";
        public const string SETUP_BASIC_DELIVERY_MODE_DESC = "setup_basic_delivery_mode_desc";
        public const string SETUP_BASIC_OBSTACLE_MODE      = "setup_basic_obstacle_mode";
        public const string SETUP_BASIC_OBSTACLE_MODE_DESC = "setup_basic_obstacle_mode_desc";
        public const string SETUP_BASIC_AUTO_RETURN        = "setup_basic_auto_return";
        public const string SETUP_BASIC_HOME_POINT         = "setup_basic_home_point";
        public const string SETUP_BASIC_HOME_POINT_DESC    = "setup_basic_home_point_desc";
        public const string SETUP_BASIC_CHARGE_POINT       = "setup_basic_charge_point";
        public const string SETUP_BASIC_CHARGE_POINT_DESC  = "setup_basic_charge_point_desc";
        // Time settings
        public const string SETUP_TIME_TITLE           = "setup_time_title";
        public const string SETUP_TIME_TAB_CHARGING    = "setup_time_tab_charging";
        public const string SETUP_TIME_TAB_WAITING     = "setup_time_tab_waiting";
        public const string SETUP_TIME_TAB_CUSTOM      = "setup_time_tab_custom";
        public const string SETUP_TIME_COL_TIME        = "setup_time_col_time";
        public const string SETUP_TIME_COL_NAME        = "setup_time_col_name";
        public const string SETUP_TIME_COL_TYPE        = "setup_time_col_type";
        public const string SETUP_TIME_COL_NUMBER      = "setup_time_col_number";
        public const string SETUP_TIME_COL_ROUTE       = "setup_time_col_route";
        public const string SETUP_TIME_COL_REPEAT      = "setup_time_col_repeat";
        public const string SETUP_TIME_COL_STATUS      = "setup_time_col_status";
        public const string SETUP_TIME_COL_ACTION      = "setup_time_col_action";
        public const string SETUP_TIME_EDIT            = "setup_time_edit";
        public const string SETUP_TIME_DELETE          = "setup_time_delete";
        public const string SETUP_TIME_VIEW            = "setup_time_view";
        // Delivery settings
        public const string SETUP_DELIVERY_WAIT_TIME           = "setup_delivery_wait_time";
        public const string SETUP_DELIVERY_WAIT_TIME_DESC      = "setup_delivery_wait_time_desc";
        public const string SETUP_DELIVERY_SPEED               = "setup_delivery_speed";
        public const string SETUP_DELIVERY_SPEED_DESC          = "setup_delivery_speed_desc";
        public const string SETUP_DELIVERY_COLLISION_DECEL     = "setup_delivery_collision_decel";
        public const string SETUP_DELIVERY_COLLISION_DECEL_DESC= "setup_delivery_collision_decel_desc";
        public const string SETUP_DELIVERY_ROTATION_SPEED      = "setup_delivery_rotation_speed";
        public const string SETUP_DELIVERY_ROTATION_SPEED_DESC = "setup_delivery_rotation_speed_desc";
        public const string SETUP_DELIVERY_WEIGHT_LIMIT        = "setup_delivery_weight_limit";
        public const string SETUP_DELIVERY_REVERSE             = "setup_delivery_reverse";
        public const string SETUP_DELIVERY_REVERSE_DESC        = "setup_delivery_reverse_desc";
        public const string SETUP_DELIVERY_VOICE_COUNTDOWN     = "setup_delivery_voice_countdown";
        public const string SETUP_DELIVERY_VOICE_COUNTDOWN_DESC= "setup_delivery_voice_countdown_desc";
        // Map settings
        public const string SETUP_MAP_TITLE = "setup_map_title";
        // System settings – extended
        public const string SETUP_SYS_PASSWORD          = "setup_sys_password";
        public const string SETUP_SYS_CHANGE_PASSWORD   = "setup_sys_change_password";
        public const string SETUP_SYS_POSITIONING       = "setup_sys_positioning";
        public const string SETUP_SYS_POSITIONING_DESC  = "setup_sys_positioning_desc";
        public const string SETUP_SYS_START_POSITIONING = "setup_sys_start_positioning";
        public const string SETUP_SYS_INFO_TITLE        = "setup_sys_info_title";
        public const string SETUP_SYS_SERIAL_LBL        = "setup_sys_serial_lbl";
        public const string SETUP_SYS_VERSION_LBL       = "setup_sys_version_lbl";
        public const string SETUP_SYS_CHECK_UPDATE      = "setup_sys_check_update";
        public const string SETUP_SYS_CHASSIS_VER_LBL   = "setup_sys_chassis_ver_lbl";
        public const string SETUP_SYS_SDK_VER_LBL       = "setup_sys_sdk_ver_lbl";
        public const string SETUP_SYS_FIRST_ACT_LBL     = "setup_sys_first_act_lbl";
        public const string SETUP_SYS_NO_DATA           = "setup_sys_no_data";

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
