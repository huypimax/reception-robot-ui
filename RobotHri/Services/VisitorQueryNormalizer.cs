using System.Text.RegularExpressions;

namespace RobotHri.Services
{
    /// <summary>
    /// Maps common speech-to-text mistakes (especially around "FabLab") to text that matches the RAG corpus and Gemini prompts.
    /// </summary>
    public static class VisitorQueryNormalizer
    {
        private static readonly HashSet<string> FabBlocklist = new(StringComparer.OrdinalIgnoreCase)
        {
            "fabric", "fabrics", "fabulous", "faberge", "fabian", "fable", "fables",
            "fabrication", "fabricated", "fabio", "fabien", "fabrice"
        };

        /// <summary>Known STT mis-hearings of "fablab" / "fab lab" as whole phrases.</summary>
        private static readonly Regex KnownMishearingRegex = new(
            @"\b(fabla|fablous|fablus|fablue|fabler|fablay|fablaw|fableb)\b|\bfab\s+la[b]?\b|\bfab\s+lab\b",
            RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

        public static string NormalizeForQna(string? raw)
        {
            if (string.IsNullOrWhiteSpace(raw))
                return string.Empty;

            var s = KnownMishearingRegex.Replace(raw, "fablab");
            s = NormalizeFabLikeTokens(s);
            return Regex.Replace(s, @"\s+", " ").Trim();
        }

        private static string NormalizeFabLikeTokens(string text)
        {
            // Only Latin runs: avoids warping Vietnamese words that contain "fab" by coincidence.
            return Regex.Replace(text, @"[A-Za-z]{4,11}", m =>
            {
                var w = m.Value.ToLowerInvariant();
                if (w.Length is < 4 or > 11)
                    return m.Value;
                if (!w.StartsWith("fab", StringComparison.Ordinal))
                    return m.Value;
                if (FabBlocklist.Contains(w) || w.StartsWith("fabric", StringComparison.Ordinal))
                    return m.Value;
                if (w.Contains("fablab", StringComparison.Ordinal))
                    return m.Value;

                var maxDist = w.Length <= 7 ? 3 : 4;
                return Levenshtein(w, "fablab") <= maxDist ? "fablab" : m.Value;
            }, RegexOptions.CultureInvariant);
        }

        private static int Levenshtein(string a, string b)
        {
            var n = a.Length;
            var m = b.Length;
            var d = new int[n + 1, m + 1];
            for (var i = 0; i <= n; i++) d[i, 0] = i;
            for (var j = 0; j <= m; j++) d[0, j] = j;
            for (var i = 1; i <= n; i++)
            {
                for (var j = 1; j <= m; j++)
                {
                    var cost = a[i - 1] == b[j - 1] ? 0 : 1;
                    d[i, j] = Math.Min(Math.Min(d[i - 1, j] + 1, d[i, j - 1] + 1), d[i - 1, j - 1] + cost);
                }
            }

            return d[n, m];
        }
    }
}
