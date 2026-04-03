using SkiaSharp;
using System.Globalization;
using System.Runtime.InteropServices;
using System.Text;

namespace RobotHri.Services
{
    /// <summary>
    /// Loads ROS-style occupancy grid maps: P5 binary PGM + map YAML (resolution, origin).
    /// </summary>
    public static class OccGridMapLoader
    {
        public static bool TryParseOccupancyYaml(string yaml, out double resolution, out double originX, out double originY)
        {
            resolution = 0;
            originX = 0;
            originY = 0;
            foreach (var rawLine in yaml.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var line = rawLine.Trim();
                if (line.StartsWith("resolution:", StringComparison.OrdinalIgnoreCase))
                {
                    var v = line["resolution:".Length..].Trim();
                    resolution = double.Parse(v, CultureInfo.InvariantCulture);
                }
                else if (line.StartsWith("origin:", StringComparison.OrdinalIgnoreCase))
                {
                    var open = line.IndexOf('[');
                    var close = line.IndexOf(']', open + 1);
                    if (open < 0 || close < 0)
                        continue;
                    var inner = line.Substring(open + 1, close - open - 1);
                    var parts = inner.Split(',');
                    if (parts.Length >= 2)
                    {
                        originX = double.Parse(parts[0].Trim(), CultureInfo.InvariantCulture);
                        originY = double.Parse(parts[1].Trim(), CultureInfo.InvariantCulture);
                    }
                }
            }

            return resolution > 0;
        }

        /// <summary>Decodes P5 (binary) PGM into a BGRA Skia bitmap.</summary>
        public static SKBitmap LoadPgmP5(Stream stream)
        {
            using var ms = new MemoryStream();
            stream.CopyTo(ms);
            var buf = ms.ToArray();
            var pos = 0;

            string ReadLine()
            {
                var start = pos;
                while (pos < buf.Length && buf[pos] != (byte)'\n')
                    pos++;
                var line = Encoding.ASCII.GetString(buf, start, pos - start).Trim();
                if (pos < buf.Length)
                    pos++;
                return line;
            }

            if (ReadLine() != "P5")
                throw new InvalidDataException("Expected P5 PGM header.");

            int w = 0, h = 0;
            while (w == 0 || h == 0)
            {
                var line = ReadLine();
                if (string.IsNullOrEmpty(line) || line.StartsWith('#'))
                    continue;
                var parts = line.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length >= 2)
                {
                    w = int.Parse(parts[0], CultureInfo.InvariantCulture);
                    h = int.Parse(parts[1], CultureInfo.InvariantCulture);
                }
            }

            var maxVal = 0;
            while (maxVal == 0)
            {
                var line = ReadLine();
                if (string.IsNullOrEmpty(line) || line.StartsWith('#'))
                    continue;
                maxVal = int.Parse(line, CultureInfo.InvariantCulture);
            }

            var pixelBytes = maxVal > 255 ? 2 : 1;
            var need = w * h * pixelBytes;
            if (pos + need > buf.Length)
                throw new InvalidDataException("PGM file is truncated.");

            var bgra = new byte[w * h * 4];
            if (pixelBytes == 1)
            {
                for (var i = 0; i < w * h; i++)
                {
                    var g = buf[pos + i];
                    var o = i * 4;
                    bgra[o] = g;
                    bgra[o + 1] = g;
                    bgra[o + 2] = g;
                    bgra[o + 3] = 255;
                }
            }
            else
            {
                for (var i = 0; i < w * h; i++)
                {
                    var v = (buf[pos + i * 2] << 8) | buf[pos + i * 2 + 1];
                    var g = (byte)(v * 255 / maxVal);
                    var o = i * 4;
                    bgra[o] = g;
                    bgra[o + 1] = g;
                    bgra[o + 2] = g;
                    bgra[o + 3] = 255;
                }
            }

            var info = new SKImageInfo(w, h, SKColorType.Bgra8888, SKAlphaType.Opaque);
            var bitmap = new SKBitmap(w, h, SKColorType.Bgra8888, SKAlphaType.Opaque);
            var dst = bitmap.GetPixels();
            if (dst == IntPtr.Zero)
                throw new InvalidOperationException("Could not allocate Skia bitmap pixels.");
            Marshal.Copy(bgra, 0, dst, bgra.Length);
            return bitmap;
        }
    }
}
