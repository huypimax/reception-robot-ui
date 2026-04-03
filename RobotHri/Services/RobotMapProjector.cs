using SkiaSharp;

namespace RobotHri.Services
{
    /// <summary>
    /// Same /map → pixel transform as Reception_Robot_GUI <c>LocationTab.update_robot_gui</c>.
    /// </summary>
    public static class RobotMapProjector
    {
        public static SKPoint WorldToMapPixel(
            double xWorld,
            double yWorld,
            double resolution,
            double originX,
            double originY,
            float mapHeightPixels)
        {
            var pyRaw = (yWorld - originY) / resolution;
            var pxRaw = (xWorld - originX) / resolution;
            var px = (float)pxRaw;
            var py = (float)(mapHeightPixels - pyRaw);
            return new SKPoint(px, py);
        }
    }
}
