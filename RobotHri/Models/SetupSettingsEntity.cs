using SQLite;

namespace RobotHri.Models
{
    public class SetupSettingsEntity
    {
        [PrimaryKey]
        public int Id { get; set; } = 1;

        public string ActiveMapName { get; set; } = "B1";

        // Basic
        public int SelectedDeliveryModeIndex { get; set; } = 1;

        // Sound
        public bool IsSoundEnabled { get; set; } = true;
        public int SoundVolume { get; set; } = 100;
        public int MusicVolume { get; set; } = 100;
        public int SpeechVolume { get; set; } = 100;
        public int ObstacleVolume { get; set; } = 100;
        public string SelectedMusic { get; set; } = "Năm Qua Đã Làm Gì.mp3";

        // Route
        public double WaitTimeSeconds { get; set; } = 120;
        public double SpeedCmS { get; set; } = 100;

        // Delivery
        public double DeliveryWaitTime { get; set; } = 107;
        public double DeliverySpeed { get; set; } = 100;
        public double CollisionDecelFactor { get; set; } = 0.8;
        public bool IsCollisionDecelEnabled { get; set; } = true;
        public double RotationSpeed { get; set; } = 1.2;
        public bool IsWeightLimitEnabled { get; set; } = false;
        public string SelectedReverseMode { get; set; } = "Lùi chủ động";
        public bool IsVoiceCountdownEnabled { get; set; } = false;

        // System
        public bool IsPasswordEnabled { get; set; } = false;
    }
}
