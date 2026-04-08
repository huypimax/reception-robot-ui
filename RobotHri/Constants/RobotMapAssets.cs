namespace RobotHri.Constants
{
    public static class RobotMapAssets
    {
        public static string CurrentMapName { get; set; } = "B1";

        /// <summary>MauiAsset logical names under Resources/Raw/Maps/</summary>
        public static string Pgm => CurrentMapName == "B2" ? "Maps/map_b2.pgm" : "Maps/map_b1.pgm";
        public static string Yaml => CurrentMapName == "B2" ? "Maps/map_b2.yaml" : "Maps/map_b1.yaml";
    }
}
