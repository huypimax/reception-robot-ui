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

            var apiKey = Environment.GetEnvironmentVariable("AIzaSyBCsbKx3x5g5DbduaBa9n01VU23U2jsi6s");
            if (string.IsNullOrWhiteSpace(apiKey))
            {
                return languageCode == "vi"
                    ? "Chua cau hinh GEMINI_API_KEY. Vui long dat bien moi truong de su dung chat AI."
                    : "GEMINI_API_KEY is missing. Set the environment variable to use AI chat.";
            }

            var contexts = RetrieveTopContexts(query, topK: 4);
            var prompt = BuildPrompt(query, languageCode, contexts);

            var model = AppConstants.ModelName;
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
                    temperature = 0.3
                }
            };

            using var response = await _httpClient.PostAsJsonAsync(endpoint, payload, cancellationToken);
            if (!response.IsSuccessStatusCode)
            {
                var errorText = await response.Content.ReadAsStringAsync(cancellationToken);
                System.Diagnostics.Debug.WriteLine($"[GeminiRagQnaService] API error: {errorText}");
                return languageCode == "vi"
                    ? "Minh chua lay duoc cau tra loi luc nay. Ban thu lai sau nhe."
                    : "I cannot get an answer right now. Please try again in a moment.";
            }

            using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
            using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: cancellationToken);
            var text = ExtractGeminiText(doc);

            if (string.IsNullOrWhiteSpace(text))
            {
                return languageCode == "vi"
                    ? "Minh chua tim thay noi dung phu hop tu nguon du lieu."
                    : "I could not find enough grounded content from the loaded sources.";
            }

            return text.Trim();
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
            foreach (var assetPath in RagAssetCandidates)
            {
                try
                {
                    await using var stream = await FileSystem.OpenAppPackageFileAsync(assetPath);
                    using var reader = new StreamReader(stream, Encoding.UTF8);
                    var json = await reader.ReadToEndAsync(cancellationToken);
                    var parsed = ParseCorpus(json);
                    if (parsed?.Count > 0)
                    {
                        System.Diagnostics.Debug.WriteLine(
                            $"[GeminiRagQnaService] Loaded {parsed.Count} chunks from asset: {assetPath}");
                        return parsed;
                    }
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
            return null;
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

        private static List<RagChunk>? ParseCorpus(string json)
        {
            return JsonSerializer.Deserialize<List<RagChunk>>(json);
        }

        private List<RagChunk> RetrieveTopContexts(string query, int topK)
        {
            var qTokens = Tokenize(query);
            return _chunks
                .Select(c => new { Chunk = c, Score = Score(qTokens, Tokenize(c.Content)) })
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
            return overlap;
        }

        private static HashSet<string> Tokenize(string text)
        {
            return Regex.Matches(text.ToLowerInvariant(), "[a-z0-9a-zA-ZÀ-ỹ_]+")
                .Select(m => m.Value)
                .Where(t => t.Length > 1)
                .ToHashSet();
        }

        private static string BuildPrompt(string query, string languageCode, IReadOnlyList<RagChunk> contexts)
        {
            var langInstruction = languageCode == "vi"
                ? "Tra loi bang tieng Viet ngan gon, lich su, de hieu."
                : "Answer in concise, friendly English.";

            var contextText = contexts.Count == 0
                ? "No retrieved context."
                : string.Join("\n\n", contexts.Select((c, i) =>
                    $"[{i + 1}] Source: {c.SourceUrl}\nTitle: {c.Title}\nContent: {c.Content}"));

            return $"""
                You are AIko, a receptionist assistant for HCMUT/FabLab visitors.
                {langInstruction}
                Use ONLY the retrieved context below for factual claims.
                If the answer is missing, say you are not sure and suggest checking official sources.
                When you provide facts, include source URLs at the end.

                Retrieved context:
                {contextText}

                User question:
                {query}
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
