using System.Collections.Concurrent;
using System.Reflection;
using System.Text.Json;

namespace RobotHri.Languages
{
    /// <summary>
    /// Core localization engine. Mirrors CloudBanking's Localize.cs pattern.
    /// Loads JSON translation files from embedded resources and provides GetString().
    /// </summary>
    public static class Localize
    {
        public static readonly List<LocaleModel> Locales = new List<LocaleModel>
        {
            new LocaleModel(1, "vi_VN", "Tiếng Việt", "vi-VN.json", true),
            new LocaleModel(2, "en_US", "English (US)", "en-US.json", false),
        };

        static readonly ConcurrentDictionary<int, IDictionary<string, string>> _dict
            = new ConcurrentDictionary<int, IDictionary<string, string>>();

        static int _currentId = 1;

        public static int CurrentLanguageId => _currentId;

        public static string CurrentLocaleCode =>
            Locales.FirstOrDefault(l => l.Id == _currentId)?.Code ?? "vi_VN";

        public static event EventHandler? LanguageChanged;

        /// <summary>
        /// Sets the active locale and loads its JSON file if not already loaded.
        /// </summary>
        public static bool SetLocalize(int languageId)
        {
            var locale = Locales.FirstOrDefault(l => l.Id == languageId);
            if (locale == null) return false;

            if (!_dict.ContainsKey(languageId))
            {
                var dict = LoadJsonFromFile(locale.FileName);
                if (dict == null) return false;
                _dict[languageId] = dict;
            }

            _currentId = languageId;
            LanguageChanged?.Invoke(null, EventArgs.Empty);
            return true;
        }

        /// <summary>
        /// Toggle between Vietnamese (1) and English (2).
        /// </summary>
        public static void ToggleLanguage()
        {
            int next = _currentId == 1 ? 2 : 1;
            SetLocalize(next);
        }

        /// <summary>
        /// Extension method: StringIds.APP_NAME.GetString()
        /// Auto-loads the active language JSON on first use if not already loaded.
        /// </summary>
        public static string GetString(this string key)
        {
            // Ensure the current locale is loaded before trying to resolve
            if (!_dict.ContainsKey(_currentId))
                SetLocalize(_currentId);

            return GetString(_currentId, key);
        }

        /// <summary>
        /// Get string for a specific language id.
        /// </summary>
        public static string GetString(int languageId, string key)
        {
            if (_dict.TryGetValue(languageId, out var dict) && dict.TryGetValue(key, out var value))
                return value;

            // Fallback: try to load and return
            if (!_dict.ContainsKey(languageId))
            {
                var locale = Locales.FirstOrDefault(l => l.Id == languageId);
                if (locale != null)
                {
                    var loaded = LoadJsonFromFile(locale.FileName);
                    if (loaded != null)
                    {
                        _dict[languageId] = loaded;
                        if (loaded.TryGetValue(key, out var fallbackValue))
                            return fallbackValue;
                    }
                }
            }
            return key;
        }

        /// <summary>
        /// Format a localized string by replacing {placeholder} tokens.
        /// Usage: StringIds.NAV_HEADING_TO.GetString().Format(("place", "Room A"))
        /// </summary>
        public static string Format(this string template, params (string key, string value)[] args)
        {
            foreach (var (key, value) in args)
                template = template.Replace($"{{{key}}}", value);
            return template;
        }

        static IDictionary<string, string>? LoadJsonFromFile(string fileName)
        {
            try
            {
                // Run on a thread-pool thread to avoid UI-thread deadlock
                // when .GetAwaiter().GetResult() is called during DI initialization.
                return Task.Run(async () =>
                {
                    using var stream = await FileSystem.OpenAppPackageFileAsync($"Languages/{fileName}");
                    if (stream == null) return null;
                    using var reader = new StreamReader(stream);
                    var json = await reader.ReadToEndAsync();
                    return JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                }).GetAwaiter().GetResult();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[Localize] Failed to load {fileName}: {ex.Message}");
                return null;
            }
        }
    }

    public class LocaleModel
    {
        public int Id { get; }
        public string Code { get; }
        public string DisplayName { get; }
        public string FileName { get; }
        public bool IsDefault { get; }

        public LocaleModel(int id, string code, string displayName, string fileName, bool isDefault)
        {
            Id = id;
            Code = code;
            DisplayName = displayName;
            FileName = fileName;
            IsDefault = isDefault;
        }
    }
}
