"""
Language Manager - Quản lý đa ngôn ngữ
"""
import os
import json
from typing import Dict, Optional


class LanguageManager:
    """Quản lý ngôn ngữ cho ứng dụng"""
    
    SUPPORTED_LANGUAGES = ["vi", "en"]
    DEFAULT_LANGUAGE = "vi"
    
    def __init__(self, language: str = None):
        """
        Khởi tạo LanguageManager
        
        Args:
            language: Ngôn ngữ mặc định ("vi" hoặc "en")
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.languages_dir = os.path.join(self.base_dir, "languages")
        self.config_file = os.path.join(self.base_dir, "config.json")
        
        # Load language preference từ config hoặc dùng default
        self.current_language = language or self._load_language_preference()
        self.translations: Dict[str, Dict] = {}
        
        # Load translations
        self._load_translations()
    
    def _load_language_preference(self) -> str:
        """Load language preference từ config.json"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    lang = config.get("language", self.DEFAULT_LANGUAGE)
                    if lang in self.SUPPORTED_LANGUAGES:
                        return lang
        except Exception as e:
            print(f"Error loading language preference: {e}")
        
        return self.DEFAULT_LANGUAGE
    
    def _save_language_preference(self, language: str):
        """Lưu language preference vào config.json"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            config["language"] = language
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving language preference: {e}")
    
    def _load_translations(self):
        """Load tất cả translations từ file JSON"""
        for lang in self.SUPPORTED_LANGUAGES:
            lang_file = os.path.join(self.languages_dir, f"{lang}.json")
            try:
                if os.path.exists(lang_file):
                    with open(lang_file, "r", encoding="utf-8") as f:
                        self.translations[lang] = json.load(f)
                else:
                    print(f"Warning: Language file {lang_file} not found")
            except Exception as e:
                print(f"Error loading language file {lang_file}: {e}")
                self.translations[lang] = {}
    
    def get(self, key: str, default: str = None, **kwargs) -> str:
        """
        Lấy translation string theo key (flat structure)
        
        Args:
            key: Key đơn giản (ví dụ: "nav_where_to_go")
            default: Giá trị mặc định nếu không tìm thấy
            **kwargs: Các biến để format string (nếu có {variable})
            
        Returns:
            Translated string
        """
        try:
            # Lấy translation trực tiếp từ flat dict
            translation = self.translations.get(self.current_language, {}).get(key)
            
            # Nếu không tìm thấy, thử fallback sang ngôn ngữ mặc định
            if not translation:
                if self.current_language != self.DEFAULT_LANGUAGE:
                    translation = self.translations.get(self.DEFAULT_LANGUAGE, {}).get(key)
            
            # Nếu vẫn không có, trả về default hoặc key
            if not translation:
                return default or key
            
            # Format string nếu có kwargs
            if isinstance(translation, str) and kwargs:
                try:
                    return translation.format(**kwargs)
                except KeyError:
                    return translation
            
            return str(translation) if translation else (default or key)
            
        except Exception as e:
            print(f"Error getting translation for key '{key}': {e}")
            return default or key
    
    def set_language(self, language: str):
        """
        Chuyển đổi ngôn ngữ
        
        Args:
            language: "vi" hoặc "en"
        """
        if language in self.SUPPORTED_LANGUAGES:
            self.current_language = language
            self._save_language_preference(language)
        else:
            print(f"Warning: Unsupported language '{language}'. Using default.")
            self.current_language = self.DEFAULT_LANGUAGE
    
    def get_current_language(self) -> str:
        """Lấy ngôn ngữ hiện tại"""
        return self.current_language
    
    def toggle_language(self):
        """Chuyển đổi giữa vi và en"""
        if self.current_language == "vi":
            self.set_language("en")
        else:
            self.set_language("vi")
    
    def get_language_name(self, language: str = None) -> str:
        """Lấy tên hiển thị của ngôn ngữ"""
        lang = language or self.current_language
        names = {
            "vi": "Tiếng Việt",
            "en": "English"
        }
        return names.get(lang, lang)


# Global instance
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """Lấy global LanguageManager instance"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def get_string(key: str, default: str = None, **kwargs) -> str:
    """
    Helper function để lấy translation nhanh
    
    Args:
        key: Translation key
        default: Default value
        **kwargs: Format variables
        
    Returns:
        Translated string
    """
    return get_language_manager().get(key, default, **kwargs)


class Translations:
    """
    Wrapper class để access translations như object properties (giống Android)
    
    Usage:
        translations = Translations(get_language_manager())
        text = translations.main_title  # Access như property
        text = translations.get('nav_heading_to', place='Room A')  # Với format
    """
    def __init__(self, lang_manager: LanguageManager):
        self._lang_manager = lang_manager
    
    def __getattr__(self, key: str):
        """Access translation như property: translations.main_title"""
        return self._lang_manager.get(key, default=key)
    
    def get(self, key: str, default: str = None, **kwargs) -> str:
        """Get translation với format variables"""
        return self._lang_manager.get(key, default, **kwargs)
    
    @property
    def current(self) -> dict:
        """Get current language translations dict (cách 1)"""
        return self._lang_manager.translations.get(
            self._lang_manager.current_language, 
            {}
        )


def get_translations() -> Translations:
    """
    Get Translations object để access như properties
    
    Usage:
        t = get_translations()
        text = t.main_title  # Thay vì get_string(stringIds.MAIN_TITLE)
    """
    return Translations(get_language_manager())


def update_widgets_auto(ui, widget_patterns: list = None):
    """
    Tự động update widgets bằng cách match widget name với JSON keys
    KHÔNG CẦN PREFIX, KHÔNG CẦN HARDCODE!
    
    Logic:
        1. Scan tất cả widgets có setText()
        2. Với mỗi widget, tìm JSON key match theo nhiều cách:
           - Exact match: widget name == JSON key
           - Partial match: JSON key chứa widget name hoặc ngược lại
           - Pattern match: widget name có thể map với JSON key
        3. Update widget nếu tìm thấy match
    
    Args:
        ui: UI object (self hoặc self.ui)
        widget_patterns: List patterns để filter widgets (mặc định: ["prompt_", "label_"])
    
    Example:
        update_widgets_auto(self.ui)  # Tự động tìm và update tất cả
    """
    lang_manager = get_language_manager()
    translations = lang_manager.translations.get(lang_manager.current_language, {})
    json_keys = list(translations.keys())
    
    if widget_patterns is None:
        widget_patterns = ["prompt_", "label_"]
    
    # Scan tất cả attributes
    for attr_name in dir(ui):
        if attr_name.startswith('_'):
            continue
        
        # Filter theo pattern nếu có
        if widget_patterns and not any(attr_name.startswith(p) for p in widget_patterns):
            continue
        
        try:
            widget = getattr(ui, attr_name)
            if not hasattr(widget, 'setText'):
                continue
            
            # Tìm JSON key match với widget name
            matched_key = None
            
            # Strategy 1: Exact match
            if attr_name in json_keys:
                matched_key = attr_name
            
            # Strategy 2: Widget name là suffix của JSON key
            # Ví dụ: prompt_main -> main_prompt_main hoặc qna_prompt_main
            if not matched_key:
                for key in json_keys:
                    if key.endswith(attr_name) or attr_name in key:
                        matched_key = key
                        break
            
            # Strategy 3: Remove common prefixes và match
            # Ví dụ: prompt_main -> main, prompt_qna -> qna
            if not matched_key:
                clean_name = attr_name
                for prefix in ["prompt_", "label_", "btn_"]:
                    if clean_name.startswith(prefix):
                        clean_name = clean_name[len(prefix):]
                        break
                
                # Tìm JSON key có chứa clean_name
                for key in json_keys:
                    if clean_name in key or key.endswith(clean_name):
                        matched_key = key
                        break
            
            # Strategy 4: Fuzzy match - tìm key có nhiều từ giống nhất
            if not matched_key:
                widget_words = set(attr_name.lower().split('_'))
                best_match = None
                best_score = 0
                
                for key in json_keys:
                    key_words = set(key.lower().split('_'))
                    common_words = widget_words & key_words
                    if len(common_words) > best_score:
                        best_score = len(common_words)
                        best_match = key
                
                if best_score > 0:
                    matched_key = best_match
            
            # Update widget nếu tìm thấy match
            if matched_key:
                widget.setText(translations[matched_key])
                    
        except Exception as e:
            continue
