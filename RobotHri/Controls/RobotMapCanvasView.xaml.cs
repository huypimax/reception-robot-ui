using RobotHri.Constants;
using RobotHri.Services;
using SkiaSharp;
using SkiaSharp.Views.Maui;
using SkiaSharp.Views.Maui.Controls;

namespace RobotHri.Controls
{
    public partial class RobotMapCanvasView : ContentView
    {
        public static readonly BindableProperty RobotXProperty = BindableProperty.Create(
            nameof(RobotX),
            typeof(double),
            typeof(RobotMapCanvasView),
            0d,
            propertyChanged: (b, _, __) => ((RobotMapCanvasView)b).InvalidateMap());

        public static readonly BindableProperty RobotYProperty = BindableProperty.Create(
            nameof(RobotY),
            typeof(double),
            typeof(RobotMapCanvasView),
            0d,
            propertyChanged: (b, _, __) => ((RobotMapCanvasView)b).InvalidateMap());

        public static readonly BindableProperty RobotThetaDegreesProperty = BindableProperty.Create(
            nameof(RobotThetaDegrees),
            typeof(double),
            typeof(RobotMapCanvasView),
            0d,
            propertyChanged: (b, _, __) => ((RobotMapCanvasView)b).InvalidateMap());

        private SKBitmap? _mapBitmap;
        private int _mapWidth;
        private int _mapHeight;
        private double _resolution = 0.05;
        private double _originX;
        private double _originY;
        private string? _loadError;
        private float _scale = 1f;
        private float _offsetX;
        private float _offsetY;
        private float _fitScale = 1f;
        private float _minScale = 0.01f;
        private float _maxScale = 100f;
        private bool _userAdjustedView;
        private bool _pendingFit = true;
        private bool _loadStarted;

        private readonly Dictionary<long, SKPoint> _touchLocations = new();
        private float _lastPinchDistance;
        private SKPoint _singleFingerLast;

        public double RobotX
        {
            get => (double)GetValue(RobotXProperty);
            set => SetValue(RobotXProperty, value);
        }

        public double RobotY
        {
            get => (double)GetValue(RobotYProperty);
            set => SetValue(RobotYProperty, value);
        }

        public double RobotThetaDegrees
        {
            get => (double)GetValue(RobotThetaDegreesProperty);
            set => SetValue(RobotThetaDegreesProperty, value);
        }

        public RobotMapCanvasView()
        {
            InitializeComponent();
            Loaded += OnLoaded;
            SizeChanged += (_, _) =>
            {
                if (!_userAdjustedView)
                    _pendingFit = true;
                InvalidateMap();
            };
#if WINDOWS
            CanvasView.HandlerChanged += OnWindowsCanvasHandlerChanged;
#endif
        }

#if WINDOWS
        private void OnWindowsCanvasHandlerChanged(object? sender, EventArgs e)
        {
            if (CanvasView.Handler?.PlatformView is not SkiaSharp.Views.Windows.SKXamlCanvas winCanvas)
                return;
            winCanvas.PointerWheelChanged -= OnWindowsPointerWheelChanged;
            winCanvas.PointerWheelChanged += OnWindowsPointerWheelChanged;
        }

        private void OnWindowsPointerWheelChanged(object sender, Microsoft.UI.Xaml.Input.PointerRoutedEventArgs e)
        {
            if (sender is not SkiaSharp.Views.Windows.SKXamlCanvas canvas)
                return;
            var pt = e.GetCurrentPoint(canvas);
            var delta = pt.Properties.MouseWheelDelta;
            if (delta == 0)
                return;
            var pos = pt.Position;
            var step = MathF.Pow(1.12f, Math.Sign(delta));
            ZoomAtCenter(step);
            InvalidateMap();
            e.Handled = true;
        }
#endif

        private async void OnLoaded(object? sender, EventArgs e)
        {
            if (_loadStarted)
                return;
            _loadStarted = true;
            await LoadMapAsync();
        }

        private static async Task<Stream> OpenMapAssetAsync(string logicalName)
        {
            try
            {
                return await FileSystem.Current.OpenAppPackageFileAsync(logicalName);
            }
            catch
            {
                var alt = logicalName.Replace('/', Path.DirectorySeparatorChar);
                return await FileSystem.Current.OpenAppPackageFileAsync(alt);
            }
        }

        private async Task LoadMapAsync()
        {
            try
            {
                using (var yamlStream = await OpenMapAssetAsync(RobotMapAssets.Yaml))
                using (var reader = new StreamReader(yamlStream))
                {
                    var yamlText = await reader.ReadToEndAsync();
                    if (!OccGridMapLoader.TryParseOccupancyYaml(yamlText, out _resolution, out _originX, out _originY))
                        _loadError = "Invalid map YAML (resolution/origin).";
                }

                using (var pgmStream = await OpenMapAssetAsync(RobotMapAssets.Pgm))
                    _mapBitmap = OccGridMapLoader.LoadPgmP5(pgmStream);
                _mapWidth = _mapBitmap.Width;
                _mapHeight = _mapBitmap.Height;
                _pendingFit = true;
            }
            catch (Exception ex)
            {
                _loadError = ex.Message;
            }

            InvalidateMap();
        }

        private void FitMapToView(float viewW, float viewH)
        {
            if (_mapBitmap is null || viewW <= 0 || viewH <= 0)
                return;

            const float pad = 8f;
            var aw = viewW - 2 * pad;
            var ah = viewH - 2 * pad;
            if (aw <= 0 || ah <= 0)
                return;

            _fitScale = Math.Min(aw / _mapWidth, ah / _mapHeight);
            _scale = _fitScale;
            _minScale = _fitScale * 0.08f;
            _maxScale = _fitScale * 48f;
            _offsetX = pad + (aw - _mapWidth * _scale) / 2f;
            _offsetY = pad + (ah - _mapHeight * _scale) / 2f;
        }

        /// <summary>Zoom toward the center of the canvas view; keeping the map centered.</summary>
        private void ZoomAtCenter(float factor)
        {
            if (_mapBitmap is null || factor <= 0)
                return;

            var viewW = CanvasView.CanvasSize.Width;
            var viewH = CanvasView.CanvasSize.Height;

            var centerX = viewW / 2f;
            var centerY = viewH / 2f;

            var mx = (centerX - _offsetX) / _scale;
            var my = (centerY - _offsetY) / _scale;
            var newScale = Math.Clamp(_scale * factor, _minScale, _maxScale);
            if (Math.Abs(newScale - _scale) < 1e-5f)
                return;

            _scale = newScale;
            _offsetX = centerX - mx * _scale;
            _offsetY = centerY - my * _scale;
            _userAdjustedView = true;
        }

        private static float Distance(SKPoint a, SKPoint b)
        {
            var dx = a.X - b.X;
            var dy = a.Y - b.Y;
            return MathF.Sqrt(dx * dx + dy * dy);
        }

        private static SKPoint Midpoint(SKPoint a, SKPoint b)
        {
            return new SKPoint((a.X + b.X) / 2f, (a.Y + b.Y) / 2f);
        }

        private bool TryGetPinchPair(out SKPoint p0, out SKPoint p1)
        {
            p0 = default;
            p1 = default;
            if (_touchLocations.Count < 2)
                return false;
            using var e = _touchLocations.Values.GetEnumerator();
            e.MoveNext();
            p0 = e.Current;
            e.MoveNext();
            p1 = e.Current;
            return true;
        }

        private void InvalidateMap()
        {
            MainThread.BeginInvokeOnMainThread(() => CanvasView.InvalidateSurface());
        }

        private void OnPaintSurface(object? sender, SkiaSharp.Views.Maui.SKPaintSurfaceEventArgs e)
        {
            var canvas = e.Surface.Canvas;
            canvas.Clear(new SKColor(40, 44, 52));

            var vw = e.Info.Width;
            var vh = e.Info.Height;

            if (_loadError is not null && _mapBitmap is null)
            {
                using var paint = new SKPaint { Color = SKColors.White, TextSize = 18, IsAntialias = true };
                canvas.DrawText(_loadError, 16, 32, paint);
                return;
            }

            if (_mapBitmap is null)
            {
                using var paint = new SKPaint { Color = SKColors.LightGray, TextSize = 18, IsAntialias = true };
                canvas.DrawText("Loading map…", 16, 32, paint);
                return;
            }

            if (_pendingFit && vw > 0 && vh > 0)
            {
                if (!_userAdjustedView)
                    FitMapToView(vw, vh);
                _pendingFit = false;
            }

            var dest = new SKRect(_offsetX, _offsetY, _offsetX + _mapWidth * _scale, _offsetY + _mapHeight * _scale);
            canvas.DrawBitmap(_mapBitmap, dest);

            var robotPx = RobotMapProjector.WorldToMapPixel(
                RobotX, RobotY, _resolution, _originX, _originY, _mapHeight);

            var sx = _offsetX + robotPx.X * _scale;
            var sy = _offsetY + robotPx.Y * _scale;

            canvas.Save();
            canvas.Translate(sx, sy);
            canvas.RotateDegrees((float)(-RobotThetaDegrees + 90));

            using var tri = new SKPath();
            tri.MoveTo(0, -15 * _scale);
            tri.LineTo(8 * _scale, 20 * _scale);
            tri.LineTo(-8 * _scale, 20 * _scale);
            tri.Close();

            using var fill = new SKPaint
            {
                Color = new SKColor(101, 230, 248),
                Style = SKPaintStyle.Fill,
                IsAntialias = true
            };
            using var stroke = new SKPaint
            {
                Color = SKColors.Black,
                Style = SKPaintStyle.Stroke,
                StrokeWidth = Math.Max(1f, _scale),
                IsAntialias = true
            };
            canvas.DrawPath(tri, fill);
            canvas.DrawPath(tri, stroke);
            canvas.Restore();
        }

        private void OnTouch(object? sender, SKTouchEventArgs e)
        {
            e.Handled = true;

            if (e.ActionType == SKTouchAction.WheelChanged)
            {
                var delta = e.WheelDelta;
                if (delta == 0)
                    return;
                var step = MathF.Pow(1.12f, Math.Sign(delta));
                ZoomAtCenter(step);
                InvalidateMap();
                return;
            }

            switch (e.ActionType)
            {
                case SKTouchAction.Pressed:
                    _touchLocations[e.Id] = e.Location;
                    _userAdjustedView = true;
                    if (_touchLocations.Count == 1)
                        _singleFingerLast = e.Location;
                    if (_touchLocations.Count >= 2 && TryGetPinchPair(out var a, out var b))
                        _lastPinchDistance = Distance(a, b);
                    break;

                case SKTouchAction.Moved:
                    _touchLocations[e.Id] = e.Location;
                    if (_touchLocations.Count >= 2 && TryGetPinchPair(out var p0, out var p1))
                    {
                        var d = Distance(p0, p1);
                        if (_lastPinchDistance > 2f)
                        {
                            var mid = Midpoint(p0, p1);
                            var factor = d / _lastPinchDistance;

                            ZoomAtCenter(factor);
                        }
                        _lastPinchDistance = d;
                    }
                    InvalidateMap();
                    break;

                case SKTouchAction.Released:
                case SKTouchAction.Cancelled:
                    _touchLocations.Remove(e.Id);
                    if (_touchLocations.Count < 2)
                        _lastPinchDistance = 0;
                    if (_touchLocations.Count == 1)
                    {
                        foreach (var kv in _touchLocations)
                        {
                            _singleFingerLast = kv.Value;
                            break;
                        }
                    }
                    break;
            }
        }
    }
}