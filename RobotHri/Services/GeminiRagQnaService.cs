using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using RobotHri.Constants;

namespace RobotHri.Services
{
    public class GeminiRagQnaService : IQnaResponseService
    {
        private static readonly string[] RagAssetCandidates =
        {
            "Rag/langgraph_rag_corpus.json",
            "Rag/hcmut_seed.json"
        };
        private readonly HttpClient _httpClient;
        private readonly SemaphoreSlim _loadLock = new(1, 1);
        private List<RagChunk> _chunks = [];

        public GeminiRagQnaService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<string> GetAnswerAsync(string query, string languageCode, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(query))
                return string.Empty;

            await EnsureCorpusLoadedAsync(cancellationToken);

            var verbatimQuery = query.Trim();
            var normalizedQuery = VisitorQueryNormalizer.NormalizeForQna(verbatimQuery);
            if (string.IsNullOrWhiteSpace(normalizedQuery))
                normalizedQuery = verbatimQuery;

            var contexts = RetrieveTopContexts(normalizedQuery, topK: 4);
            var hasLocalContext = contexts.Count > 0;

            var apiKey = Environment.GetEnvironmentVariable("GEMINI_API_KEY");
            if (string.IsNullOrWhiteSpace(apiKey))
            {
                if (hasLocalContext)
                    return BuildLocalRagFallbackAnswer(contexts, languageCode, LocalFallbackReason.MissingApiKey);
                return languageCode == "vi"
                    ? "Chua cau hinh GEMINI_API_KEY. Vui long dat bien moi truong de su dung chat AI."
                    : "GEMINI_API_KEY is missing. Set the environment variable to use AI chat.";
            }

            var prompt = hasLocalContext
                ? BuildGroundedRagPrompt(verbatimQuery, normalizedQuery, languageCode, contexts)
                : BuildHcmutGeminiPrompt(verbatimQuery, normalizedQuery, languageCode);

            var model = Environment.GetEnvironmentVariable("GEMINI_MODEL");
            if (string.IsNullOrWhiteSpace(model))
                model = AppConstants.ModelName;

            var endpoint = $"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={apiKey}";

            var payload = new
            {
                contents = new[]
                {
                    new
                    {
                        role = "user",
                        parts = new[] { new { text = prompt } }
                    }
                },
                generationConfig = new
                {
                    temperature = hasLocalContext ? 0.3 : 0.45
                }
            };

            try
            {
                using var response = await _httpClient.PostAsJsonAsync(endpoint, payload, cancellationToken);
                if (!response.IsSuccessStatusCode)
                {
                    var errorText = await response.Content.ReadAsStringAsync(cancellationToken);
                    System.Diagnostics.Debug.WriteLine($"[GeminiRagQnaService] API error: {errorText}");
                    if (hasLocalContext)
                        return BuildLocalRagFallbackAnswer(contexts, languageCode, LocalFallbackReason.GeminiHttpError, response.StatusCode);
                    return FormatApiUserMessage(languageCode, response.StatusCode, errorText);
                }

                using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
                using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: cancellationToken);
                var text = ExtractGeminiText(doc);

                if (!string.IsNullOrWhiteSpace(text))
                    return text.Trim();

                if (hasLocalContext)
                    return BuildLocalRagFallbackAnswer(contexts, languageCode, LocalFallbackReason.EmptyGeminiReply);

                return languageCode == "vi"
                    ? "Minh chua lay duoc cau tra loi. Ban thu hoi ro hon hoac kiem tra mang."
                    : "I could not generate an answer. Please try rephrasing or check your connection.";
            }
            catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException or OperationCanceledException)
            {
                System.Diagnostics.Debug.WriteLine($"[GeminiRagQnaService] Request failed: {ex.Message}");
                if (hasLocalContext)
                    return BuildLocalRagFallbackAnswer(contexts, languageCode, LocalFallbackReason.NetworkError);
                return languageCode == "vi"
                    ? "Loi mang hoac het thoi gian cho. Ban thu lai sau."
                    : "Network error or timeout. Please try again.";
            }
        }

        private enum LocalFallbackReason
        {
            MissingApiKey,
            GeminiHttpError,
            EmptyGeminiReply,
            NetworkError
        }

        private static string BuildLocalRagFallbackAnswer(
            IReadOnlyList<RagChunk> contexts,
            string languageCode,
            LocalFallbackReason reason,
            HttpStatusCode statusCode = default)
        {
            var header = (languageCode, reason) switch
            {
                ("vi", LocalFallbackReason.MissingApiKey) =>
                    "Chua cau hinh GEMINI_API_KEY. Duoi day la thong tin tim duoc trong du lieu cuc bo (chua qua AI):",
                (_, LocalFallbackReason.MissingApiKey) =>
                    "GEMINI_API_KEY is not set. Here is what I found in local campus data (not AI-polished):",
                ("vi", LocalFallbackReason.GeminiHttpError) =>
                    statusCode == HttpStatusCode.TooManyRequests
                        ? "Dich vu Gemini tam bi gioi han (quota). Duoi day la thong tin tim duoc trong du lieu cuc bo:"
                        : "Khong goi duoc Gemini. Duoi day la thong tin tim duoc trong du lieu cuc bo:",
                (_, LocalFallbackReason.GeminiHttpError) =>
                    statusCode == HttpStatusCode.TooManyRequests
                        ? "Gemini is rate-limited or over quota. Here is what I found in local data:"
                        : "The Gemini request failed. Here is what I found in local data:",
                ("vi", LocalFallbackReason.EmptyGeminiReply) =>
                    "Gemini khong tra loi. Duoi day la thong tin tim duoc trong du lieu cuc bo:",
                (_, LocalFallbackReason.EmptyGeminiReply) =>
                    "Gemini returned no text. Here is what I found in local data:",
                ("vi", LocalFallbackReason.NetworkError) =>
                    "Loi mang. Duoi day la thong tin tim duoc trong du lieu cuc bo:",
                (_, LocalFallbackReason.NetworkError) =>
                    "Network issue. Here is what I found in local data:",
                _ => languageCode == "vi"
                    ? "Duoi day la thong tin tim duoc trong du lieu cuc bo:"
                    : "Here is what I found in local data:"
            };

            const int maxChunks = 3;
            const int excerptLen = 480;
            var sb = new StringBuilder();
            sb.AppendLine(header);
            sb.AppendLine();

            var n = Math.Min(maxChunks, contexts.Count);
            for (var i = 0; i < n; i++)
            {
                var c = contexts[i];
                sb.AppendLine($"— {(string.IsNullOrWhiteSpace(c.Title) ? "Source" : c.Title)}");
                if (!string.IsNullOrWhiteSpace(c.SourceUrl))
                    sb.AppendLine(c.SourceUrl);
                var excerpt = SummarizeChunkBody(c.Content, excerptLen);
                if (!string.IsNullOrWhiteSpace(excerpt))
                    sb.AppendLine(excerpt);
                sb.AppendLine();
            }

            sb.Append(languageCode == "vi"
                ? "Vui long doi chieu chi tiet tren cac lien ket chinh thuc."
                : "Please double-check details on the official links above.");
            return sb.ToString().Trim();
        }

        private static string SummarizeChunkBody(string content, int maxLen)
        {
            if (string.IsNullOrWhiteSpace(content))
                return string.Empty;
            var oneLine = Regex.Replace(content.Trim(), @"\s+", " ");
            if (oneLine.Length <= maxLen)
                return oneLine;
            return oneLine[..maxLen].TrimEnd() + "…";
        }

        private async Task EnsureCorpusLoadedAsync(CancellationToken cancellationToken)
        {
            if (_chunks.Count > 0) return;

            await _loadLock.WaitAsync(cancellationToken);
            try
            {
                if (_chunks.Count > 0) return;
                var loaded = await LoadFromAppAssetsAsync(cancellationToken)
                    ?? await LoadFromExternalFileAsync(cancellationToken);
                _chunks = loaded?.Where(c => !string.IsNullOrWhiteSpace(c.Content)).ToList() ?? [];
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[GeminiRagQnaService] Load corpus failed: {ex.Message}");
                _chunks = [];
            }
            finally
            {
                _loadLock.Release();
            }
        }

        private async Task<List<RagChunk>?> LoadFromAppAssetsAsync(CancellationToken cancellationToken)
        {
            // Load all bundled corpora in order: primary (langgraph) first, then supplements.
            var merged = new List<RagChunk>();
            var seenKeys = new HashSet<string>();
            foreach (var assetPath in RagAssetCandidates)
            {
                try
                {
                    await using var stream = await FileSystem.OpenAppPackageFileAsync(assetPath);
                    using var reader = new StreamReader(stream, Encoding.UTF8);
                    var json = await reader.ReadToEndAsync(cancellationToken);
                    var parsed = ParseCorpus(json);
                    if (parsed == null || parsed.Count == 0)
                        continue;

                    var added = 0;
                    foreach (var c in parsed)
                    {
                        if (string.IsNullOrWhiteSpace(c.Content))
                            continue;
                        var key = $"{c.SourceUrl}\u001f{c.Title}\u001f{c.Content}";
                        if (!seenKeys.Add(key))
                            continue;
                        merged.Add(c);
                        added++;
                    }

                    System.Diagnostics.Debug.WriteLine(
                        $"[GeminiRagQnaService] Loaded {added} new chunks ({parsed.Count} in file) from asset: {assetPath}");
                }
                catch (FileNotFoundException)
                {
                    // Try next candidate.
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine(
                        $"[GeminiRagQnaService] Failed to load asset '{assetPath}': {ex.Message}");
                }
            }

            return merged.Count > 0 ? merged : null;
        }

        private async Task<List<RagChunk>?> LoadFromExternalFileAsync(CancellationToken cancellationToken)
        {
            var configuredPath = Environment.GetEnvironmentVariable("RAG_CORPUS_PATH");
            if (string.IsNullOrWhiteSpace(configuredPath) || !File.Exists(configuredPath))
                return null;

            var json = await File.ReadAllTextAsync(configuredPath, cancellationToken);
            var parsed = ParseCorpus(json);
            if (parsed?.Count > 0)
            {
                System.Diagnostics.Debug.WriteLine(
                    $"[GeminiRagQnaService] Loaded {parsed.Count} chunks from external file: {configuredPath}");
            }
            return parsed;
        }

        /// <summary>Corpus JSON uses camelCase (title, sourceUrl, content); defaults must match or all chunks deserialize empty.</summary>
        private static readonly JsonSerializerOptions CorpusJsonOptions = new()
        {
            PropertyNameCaseInsensitive = true,
            ReadCommentHandling = JsonCommentHandling.Skip,
            AllowTrailingCommas = true,
        };

        private static List<RagChunk>? ParseCorpus(string json)
        {
            return JsonSerializer.Deserialize<List<RagChunk>>(json, CorpusJsonOptions);
        }

        private static string FormatApiUserMessage(string languageCode, HttpStatusCode status, string errorJson)
        {
            if (status == HttpStatusCode.TooManyRequests || errorJson.Contains("\"code\": 429", StringComparison.Ordinal))
            {
                var wait = TryExtractRetrySecondsHint(errorJson, languageCode);
                return languageCode == "vi"
                    ? $"API Gemini bi gioi han (429 — het quota hoac qua nhieu yeu cau).{wait} Vui long doi roi thu lai, kiem tra goi cuoc / billing tren Google AI Studio, hoac dat bien moi truong GEMINI_MODEL sang model khac (vi du gemini-1.5-flash)."
                    : $"The Gemini API is rate-limited or your quota is exhausted (429).{wait} Wait and try again, check your plan at Google AI Studio, or set GEMINI_MODEL to another model (e.g. gemini-1.5-flash).";
            }

            return languageCode == "vi"
                ? "Minh chua lay duoc cau tra loi luc nay. Ban thu lai sau nhe."
                : "I cannot get an answer right now. Please try again in a moment.";
        }

        private static string TryExtractRetrySecondsHint(string errorJson, string languageCode)
        {
            var m = Regex.Match(errorJson, @"retry in ([\d.]+)\s*s", RegexOptions.IgnoreCase);
            if (!m.Success)
                return string.Empty;
            var raw = m.Groups[1].Value;
            var secs = int.TryParse(raw.Split('.')[0], out var whole) ? whole.ToString() : raw.TrimEnd('.', '0');
            return languageCode == "vi"
                ? $" Ban co the thu lai sau khoang {secs} giay."
                : $" You can try again in about {secs} seconds.";
        }

        private List<RagChunk> RetrieveTopContexts(string normalizedQuery, int topK)
        {
            var qTokens = TokenizeForRetrieval(normalizedQuery);
            if (normalizedQuery.Contains("fablab", StringComparison.OrdinalIgnoreCase))
            {
                foreach (var extra in new[] { "innovation", "tbi", "hcmut", "bach", "khoa" })
                    qTokens.Add(extra);
            }

            return _chunks
                .Select(c => new { Chunk = c, Score = Score(qTokens, TokenizePlain(c.Content)) })
                .Where(x => x.Score > 0)
                .OrderByDescending(x => x.Score)
                .ThenByDescending(x => x.Chunk.Content.Length)
                .Take(topK)
                .Select(x => x.Chunk)
                .ToList();
        }

        private static int Score(HashSet<string> queryTokens, HashSet<string> docTokens)
        {
            var overlap = queryTokens.Intersect(docTokens).Count();
            if (overlap > 0)
                return overlap;

            // Spoken queries often split compounds ("fab lab") while sources use "fablab" / CamelCase runs.
            foreach (var qt in queryTokens)
            {
                if (qt.Length < 3)
                    continue;
                foreach (var dt in docTokens)
                {
                    if (dt.Contains(qt, StringComparison.Ordinal))
                        return 1;
                }
            }

            return 0;
        }

        /// <summary>
        /// Tokens for scoring chunk relevance. Includes adjacent token joins so phrases like
        /// "fab lab" overlap corpus text that only contains "fablab".
        /// </summary>
        private static HashSet<string> TokenizeForRetrieval(string text)
        {
            var ordered = Regex.Matches(text.ToLowerInvariant(), "[a-z0-9a-zA-ZÀ-ỹ_]+")
                .Select(m => m.Value)
                .Where(t => t.Length > 1)
                .ToList();

            var set = ordered.ToHashSet();
            const int maxGlueLen = 5;
            for (int span = 2; span <= Math.Min(4, ordered.Count); span++)
            {
                for (int i = 0; i + span <= ordered.Count; i++)
                {
                    var slice = ordered.GetRange(i, span);
                    if (slice.All(p => p.Length <= maxGlueLen))
                        set.Add(string.Concat(slice));
                }
            }

            return set;
        }

        private static HashSet<string> TokenizePlain(string text)
        {
            return Regex.Matches(text.ToLowerInvariant(), "[a-z0-9a-zA-ZÀ-ỹ_]+")
                .Select(m => m.Value)
                .Where(t => t.Length > 1)
                .ToHashSet();
        }

        private static string BuildGroundedRagPrompt(
            string verbatimQuery,
            string normalizedQuery,
            string languageCode,
            IReadOnlyList<RagChunk> contexts)
        {
            var langInstruction = languageCode == "vi"
                ? "Tra loi bang tieng Viet ngan gon, lich su, de hieu."
                : "Answer in concise, friendly English.";

            var speechNote = !string.Equals(verbatimQuery, normalizedQuery, StringComparison.Ordinal)
                ? (languageCode == "vi"
                    ? $"\nGhi chu nhan dang giong noi: nguoi dung noi gan giong \"{verbatimQuery}\", he thong hieu la chu de FabLab/HCMUT neu cau da duoc chuan hoa thanh \"{normalizedQuery}\"."
                    : $"\nSpeech note: the user likely asked about FabLab/HCMUT; raw recognition was \"{verbatimQuery}\" and it was normalized for search as \"{normalizedQuery}\".")
                : string.Empty;

            var contextText = string.Join("\n\n", contexts.Select((c, i) =>
                $"[{i + 1}] Source: {c.SourceUrl}\nTitle: {c.Title}\nContent: {c.Content}"));

            return $"""
                You are AIko, a receptionist assistant for HCMUT/FabLab visitors.
                {langInstruction}
                Use ONLY the retrieved context below for factual claims.
                If the answer is missing, say you are not sure and suggest checking official sources.
                When you provide facts, include source URLs at the end.

                Retrieved context:
                {contextText}
                {speechNote}

                User question (use normalized wording for intent):
                {normalizedQuery}
                """;
        }

        /// <summary>
        /// When no local RAG chunk matched, answer from Gemini general knowledge with an HCMUT keyword focus.
        /// </summary>
        private static string BuildHcmutGeminiPrompt(string verbatimQuery, string normalizedQuery, string languageCode)
        {
            var langInstruction = languageCode == "vi"
                ? "Tra loi bang tieng Viet ngan gon, lich su, de hieu."
                : "Answer in concise, friendly English.";

            return $"""
                You are AIko, a receptionist assistant for visitors to HCMUT (Ho Chi Minh City University of Technology).
                Keyword focus: HCMUT, ĐHBK, Bach Khoa, FabLab / Innovation FabLab, TBI, campuses (e.g. 268 Ly Thuong Kiet, Di An).
                The on-device RAG corpus did not return a matching excerpt for this question.
                Use careful general knowledge; prioritize facts about HCMUT and its FabLab / innovation ecosystem when the question fits.
                If the question is not about the university, answer briefly and neutrally. If you are unsure, say so and suggest checking https://hcmut.edu.vn/ or official FabLab/TBI pages.
                {langInstruction}

                Raw speech recognition (may contain errors):
                {verbatimQuery}

                Normalized / interpreted question (use for meaning):
                {normalizedQuery}
                """;
        }

        private static string? ExtractGeminiText(JsonDocument doc)
        {
            if (!doc.RootElement.TryGetProperty("candidates", out var candidates) ||
                candidates.ValueKind != JsonValueKind.Array)
            {
                return null;
            }

            foreach (var candidate in candidates.EnumerateArray())
            {
                if (!candidate.TryGetProperty("content", out var content)) continue;
                if (!content.TryGetProperty("parts", out var parts) || parts.ValueKind != JsonValueKind.Array) continue;
                foreach (var part in parts.EnumerateArray())
                {
                    if (part.TryGetProperty("text", out var text) && text.ValueKind == JsonValueKind.String)
                    {
                        return text.GetString();
                    }
                }
            }

            return null;
        }

        private sealed class RagChunk
        {
            public string Title { get; set; } = string.Empty;
            public string SourceUrl { get; set; } = string.Empty;
            public string Content { get; set; } = string.Empty;
        }
    }
}
