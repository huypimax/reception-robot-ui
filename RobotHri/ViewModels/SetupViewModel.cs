using RobotHri.Constants;
using RobotHri.Languages;
using RobotHri.Models;
using RobotHri.Services;

namespace RobotHri.ViewModels
{
    public enum SetupSection
    {
        Basic, Sound, Voice, Delivery, Route, Time, Map, Expression, System, Other, Upgrade, Developer
    }

    public class SetupViewModel : BaseViewModel
    {
        private readonly IMqttService _mqtt;

        // ─── Live robot map (admin: Setup → Map, inline panel) ─────────────────────

        private string _mapPoseSummary = string.Empty;
        private string _mapPanHint = string.Empty;
        private double _robotMapX;
        private double _robotMapY;
        private double _robotMapThetaDegrees;
        private bool _hasMapPose;

        public string MapPoseSummary
        {
            get => _mapPoseSummary;
            set => SetProperty(ref _mapPoseSummary, value);
        }

        public string MapPanHint
        {
            get => _mapPanHint;
            set => SetProperty(ref _mapPanHint, value);
        }

        public double RobotMapX
        {
            get => _robotMapX;
            set => SetProperty(ref _robotMapX, value);
        }

        public double RobotMapY
        {
            get => _robotMapY;
            set => SetProperty(ref _robotMapY, value);
        }

        public double RobotMapThetaDegrees
        {
            get => _robotMapThetaDegrees;
            set => SetProperty(ref _robotMapThetaDegrees, value);
        }

        public bool IsMapB1Selected
        {
            get => RobotMapAssets.CurrentMapName == "B1";
            set
            {
                if (value)
                {
                    RobotMapAssets.CurrentMapName = "B1";
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(IsMapB2Selected));
                    // Force the map to reload
                    OnPropertyChanged(nameof(MapTriggerReload));
                }
            }
        }

        public bool IsMapB2Selected
        {
            get => RobotMapAssets.CurrentMapName == "B2";
            set
            {
                if (value)
                {
                    RobotMapAssets.CurrentMapName = "B2";
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(IsMapB1Selected));
                    // Force the map to reload
                    OnPropertyChanged(nameof(MapTriggerReload));
                }
            }
        }

        // Just a dummy property we can bind to force the view to update
        public string MapTriggerReload => RobotMapAssets.CurrentMapName;

        // ─── Section selection ────────────────────────────────────────────────────

        private SetupSection _selectedSection = SetupSection.Route;
        public SetupSection SelectedSection
        {
            get => _selectedSection;
            set
            {
                if (!SetProperty(ref _selectedSection, value))
                    return;
                NotifySelectionBools();
                if (value == SetupSection.Map)
                    _ = TryConnectMqttForMapAsync();
            }
        }

        public bool IsBasicSelected      => SelectedSection == SetupSection.Basic;
        public bool IsSoundSelected      => SelectedSection == SetupSection.Sound;
        public bool IsVoiceSelected      => SelectedSection == SetupSection.Voice;
        public bool IsDeliverySelected   => SelectedSection == SetupSection.Delivery;
        public bool IsRouteSelected      => SelectedSection == SetupSection.Route;
        public bool IsTimeSelected       => SelectedSection == SetupSection.Time;
        public bool IsMapSelected        => SelectedSection == SetupSection.Map;
        public bool IsExpressionSelected => SelectedSection == SetupSection.Expression;
        public bool IsSystemSelected     => SelectedSection == SetupSection.System;
        public bool IsOtherSelected      => SelectedSection == SetupSection.Other;
        public bool IsUpgradeSelected    => SelectedSection == SetupSection.Upgrade;
        public bool IsDeveloperSelected  => SelectedSection == SetupSection.Developer;

        public bool IsPlaceholderSelected =>
            SelectedSection != SetupSection.Route &&
            SelectedSection != SetupSection.System &&
            SelectedSection != SetupSection.Basic &&
            SelectedSection != SetupSection.Sound &&
            SelectedSection != SetupSection.Time &&
            SelectedSection != SetupSection.Delivery &&
            SelectedSection != SetupSection.Map;

        // ─── Route settings ───────────────────────────────────────────────────────

        private double _waitTimeSeconds = 120;
        public double WaitTimeSeconds { get => _waitTimeSeconds; set => SetProperty(ref _waitTimeSeconds, value); }

        private double _speedCmS = 100;
        public double SpeedCmS    { get => _speedCmS;           set => SetProperty(ref _speedCmS, value); }

        // ─── System info ──────────────────────────────────────────────────────────

        public string NetworkSsid { get; set; } = "—";
        public string MacHead     { get; set; } = "—";
        public string IpHead      { get; set; } = "—";
        public string MacWlan     { get; set; } = "—";
        public string IpWlan      { get; set; } = "—";
        public string MacChassis  { get; set; } = "—";
        public string Imei        { get; set; } = "—";

        // ─── Sound settings ───────────────────────────────────────────────────────

        private bool _isSoundEnabled = true;
        public bool IsSoundEnabled { get => _isSoundEnabled; set => SetProperty(ref _isSoundEnabled, value); }

        private int _soundVolume   = 100;
        private int _musicVolume   = 100;
        private int _speechVolume  = 100;
        private int _obstacleVolume = 100;

        public int SoundVolume    { get => _soundVolume;    set => SetProperty(ref _soundVolume, value); }
        public int MusicVolume    { get => _musicVolume;    set => SetProperty(ref _musicVolume, value); }
        public int SpeechVolume   { get => _speechVolume;   set => SetProperty(ref _speechVolume, value); }
        public int ObstacleVolume { get => _obstacleVolume; set => SetProperty(ref _obstacleVolume, value); }

        private string _selectedMusic = "Năm Qua Đã Làm Gì.mp3";
        public string SelectedMusic { get => _selectedMusic; set => SetProperty(ref _selectedMusic, value); }

        // ─── Basic settings ───────────────────────────────────────────────────────

        private int _selectedDeliveryModeIndex = 1;   // 0=Fast 1=Multi 2=Direct 3=Route 4=Custom
        public int SelectedDeliveryModeIndex
        {
            get => _selectedDeliveryModeIndex;
            set
            {
                if (SetProperty(ref _selectedDeliveryModeIndex, value))
                {
                    NotifyDeliveryModeBools();
                    UpdateDeliveryModeText();
                }
            }
        }

        public bool IsFastModeSelected   => SelectedDeliveryModeIndex == 0;
        public bool IsMultiModeSelected  => SelectedDeliveryModeIndex == 1;
        public bool IsDirectModeSelected => SelectedDeliveryModeIndex == 2;
        public bool IsRouteModeSelected  => SelectedDeliveryModeIndex == 3;
        public bool IsCustomModeSelected => SelectedDeliveryModeIndex == 4;

        private string _selectedDeliveryModeText  = string.Empty;
        private string _selectedObstacleModeText  = "Chế độ tránh chướng ngại vật linh hoạt";
        private string _selectedAutoReturnText     = "Tắt";
        private string _selectedHomePointText      = "Trạm sạc";
        private string _selectedChargePointText    = "1-Trạm sạc";

        public string SelectedDeliveryModeText { get => _selectedDeliveryModeText;  set => SetProperty(ref _selectedDeliveryModeText, value); }
        public string SelectedObstacleModeText { get => _selectedObstacleModeText;  set => SetProperty(ref _selectedObstacleModeText, value); }
        public string SelectedAutoReturnText   { get => _selectedAutoReturnText;    set => SetProperty(ref _selectedAutoReturnText, value); }
        public string SelectedHomePointText    { get => _selectedHomePointText;     set => SetProperty(ref _selectedHomePointText, value); }
        public string SelectedChargePointText  { get => _selectedChargePointText;   set => SetProperty(ref _selectedChargePointText, value); }

        // ─── Time settings ────────────────────────────────────────────────────────

        private int _selectedTimeTabIndex;
        public int SelectedTimeTabIndex
        {
            get => _selectedTimeTabIndex;
            set
            {
                if (SetProperty(ref _selectedTimeTabIndex, value))
                    NotifyTimeTabBools();
            }
        }

        public bool IsChargingTabSelected => SelectedTimeTabIndex == 0;
        public bool IsWaitingTabSelected  => SelectedTimeTabIndex == 1;
        public bool IsCustomTabSelected   => SelectedTimeTabIndex == 2;

        public List<TimeTask> TimeTasks { get; } = new()
        {
            new() { Index = 1, Time = "05:00", TaskName = "Sạc điện", TaskType = "Thời gian", Number = "1", Route = "Trạm sạc", Repeat = "7 ngày" },
            new() { Index = 2, Time = "23:00", TaskName = "Sạc điện", TaskType = "Thời gian *", Number = "1", Route = "Trạm sạc", Repeat = "7 ngày" },
            new() { Index = 3, Time = "17:00", TaskName = "Sạc điện", TaskType = "Thời gian", Number = "1", Route = "Trạm sạc", Repeat = "7 ngày" },
            new() { Index = 4, Time = "11:00", TaskName = "Sạc điện", TaskType = "Thời gian", Number = "1", Route = "Trạm sạc", Repeat = "7 ngày" },
        };

        // ─── Delivery settings ────────────────────────────────────────────────────

        private double _deliveryWaitTime     = 107;
        private double _deliverySpeed        = 100;
        private double _collisionDecelFactor = 0.8;
        private bool   _isCollisionDecelEnabled = true;
        private double _rotationSpeed        = 1.2;
        private bool   _isWeightLimitEnabled = false;
        private string _selectedReverseMode  = "Lùi chủ động";
        private bool   _isVoiceCountdownEnabled = false;

        public double DeliveryWaitTime          { get => _deliveryWaitTime;          set => SetProperty(ref _deliveryWaitTime, value); }
        public double DeliverySpeed             { get => _deliverySpeed;             set => SetProperty(ref _deliverySpeed, value); }
        public double CollisionDecelFactor      { get => _collisionDecelFactor;      set => SetProperty(ref _collisionDecelFactor, value); }
        public bool   IsCollisionDecelEnabled   { get => _isCollisionDecelEnabled;   set => SetProperty(ref _isCollisionDecelEnabled, value); }
        public double RotationSpeed             { get => _rotationSpeed;             set => SetProperty(ref _rotationSpeed, value); }
        public bool   IsWeightLimitEnabled      { get => _isWeightLimitEnabled;      set => SetProperty(ref _isWeightLimitEnabled, value); }
        public string SelectedReverseMode       { get => _selectedReverseMode;       set => SetProperty(ref _selectedReverseMode, value); }
        public bool   IsVoiceCountdownEnabled   { get => _isVoiceCountdownEnabled;   set => SetProperty(ref _isVoiceCountdownEnabled, value); }

        // ─── System settings – extended ───────────────────────────────────────────

        private bool _isPasswordEnabled = false;
        public bool IsPasswordEnabled { get => _isPasswordEnabled; set => SetProperty(ref _isPasswordEnabled, value); }

        public string RobotSerial     { get; set; } = "2382404203023ML";
        public string RobotVersion    { get; set; } = "3.9.4 (260105(058f01)-176)";
        public string ChassisVersion  { get; set; } = "2.12.19-pi64 / 1.3.85";
        public string SdkVersion      { get; set; } = "1.1.225";

        // ─── Localized strings ────────────────────────────────────────────────────
        #region Language
        private string _titleText        = string.Empty;
        private string _exitText         = string.Empty;
        private string _navBasicText     = string.Empty;
        private string _navSoundText     = string.Empty;
        private string _navVoiceText     = string.Empty;
        private string _navDeliveryText  = string.Empty;
        private string _navRouteText     = string.Empty;
        private string _navTimeText      = string.Empty;
        private string _navMapText       = string.Empty;
        private string _navExpressionText = string.Empty;
        private string _navSystemText    = string.Empty;
        private string _navOtherText     = string.Empty;
        private string _navUpgradeText   = string.Empty;
        private string _navDeveloperText = string.Empty;
        private string _routeWaitLbl     = string.Empty;
        private string _routeWaitDesc    = string.Empty;
        private string _routeSpeedLbl    = string.Empty;
        private string _routeSpeedDesc   = string.Empty;
        private string _sysNetworkTitle  = string.Empty;
        private string _sysSsidLbl       = string.Empty;
        private string _sysMacHeadLbl    = string.Empty;
        private string _sysIpHeadLbl     = string.Empty;
        private string _sysMacWlanLbl    = string.Empty;
        private string _sysIpWlanLbl     = string.Empty;
        private string _sysMacChassisLbl = string.Empty;
        private string _sysImeiLbl       = string.Empty;
        private string _sysFactoryTitle  = string.Empty;
        private string _sysFactoryDesc   = string.Empty;
        private string _sysFactoryBtn    = string.Empty;
        private string _comingSoonText   = string.Empty;
        private string _languageLabel    = "VI";
        // Sound localized
        private string _soundToggleLbl     = string.Empty;
        private string _soundOnText        = string.Empty;
        private string _soundOffText       = string.Empty;
        private string _soundVolumeLbl     = string.Empty;
        private string _soundMusicLbl      = string.Empty;
        private string _soundSpeechLbl     = string.Empty;
        private string _soundObstacleLbl   = string.Empty;
        private string _soundChooseMusicLbl = string.Empty;
        // Basic localized
        private string _basicTitle             = string.Empty;
        private string _basicModeFast          = string.Empty;
        private string _basicModeMulti         = string.Empty;
        private string _basicModeDirect        = string.Empty;
        private string _basicModeRoute         = string.Empty;
        private string _basicModeCustom        = string.Empty;
        private string _basicDeliveryModeLbl   = string.Empty;
        private string _basicDeliveryModeDesc  = string.Empty;
        private string _basicObstacleModeLbl   = string.Empty;
        private string _basicObstacleModeDesc  = string.Empty;
        private string _basicAutoReturnLbl     = string.Empty;
        private string _basicHomePointLbl      = string.Empty;
        private string _basicHomePointDesc     = string.Empty;
        private string _basicChargePointLbl    = string.Empty;
        private string _basicChargePointDesc   = string.Empty;
        // Time localized
        private string _timeSectionTitle  = string.Empty;
        private string _timeTabCharging   = string.Empty;
        private string _timeTabWaiting    = string.Empty;
        private string _timeTabCustom     = string.Empty;
        private string _timeColTime       = string.Empty;
        private string _timeColName       = string.Empty;
        private string _timeColType       = string.Empty;
        private string _timeColNumber     = string.Empty;
        private string _timeColRoute      = string.Empty;
        private string _timeColRepeat     = string.Empty;
        private string _timeColStatus     = string.Empty;
        private string _timeColAction     = string.Empty;
        private string _timeEditText      = string.Empty;
        private string _timeDeleteText    = string.Empty;
        private string _timeViewText      = string.Empty;
        // Delivery localized
        private string _deliveryWaitTimeLbl           = string.Empty;
        private string _deliveryWaitTimeDesc          = string.Empty;
        private string _deliverySpeedLbl              = string.Empty;
        private string _deliverySpeedDesc             = string.Empty;
        private string _deliveryCollisionDecelLbl     = string.Empty;
        private string _deliveryCollisionDecelDesc    = string.Empty;
        private string _deliveryRotationSpeedLbl      = string.Empty;
        private string _deliveryRotationSpeedDesc     = string.Empty;
        private string _deliveryWeightLimitLbl        = string.Empty;
        private string _deliveryReverseLbl            = string.Empty;
        private string _deliveryReverseDesc           = string.Empty;
        private string _deliveryVoiceCountdownLbl     = string.Empty;
        private string _deliveryVoiceCountdownDesc    = string.Empty;
        // Map localized
        private string _mapTitle = string.Empty;
        // System extended localized
        private string _sysPasswordLbl         = string.Empty;
        private string _sysChangePasswordBtn   = string.Empty;
        private string _sysPositioningLbl      = string.Empty;
        private string _sysPositioningDesc     = string.Empty;
        private string _sysStartPositioningBtn = string.Empty;
        private string _sysInfoTitle           = string.Empty;
        private string _sysSerialLbl           = string.Empty;
        private string _sysVersionLbl          = string.Empty;
        private string _sysCheckUpdateBtn      = string.Empty;
        private string _sysChassisVersionLbl   = string.Empty;
        private string _sysSdkVersionLbl       = string.Empty;
        private string _sysFirstActivationLbl  = string.Empty;
        private string _sysNoDataText          = string.Empty;

        public string TitleText          { get => _titleText;          set => SetProperty(ref _titleText, value); }
        public string ExitText           { get => _exitText;           set => SetProperty(ref _exitText, value); }
        public string NavBasicText       { get => _navBasicText;       set => SetProperty(ref _navBasicText, value); }
        public string NavSoundText       { get => _navSoundText;       set => SetProperty(ref _navSoundText, value); }
        public string NavVoiceText       { get => _navVoiceText;       set => SetProperty(ref _navVoiceText, value); }
        public string NavDeliveryText    { get => _navDeliveryText;    set => SetProperty(ref _navDeliveryText, value); }
        public string NavRouteText       { get => _navRouteText;       set => SetProperty(ref _navRouteText, value); }
        public string NavTimeText        { get => _navTimeText;        set => SetProperty(ref _navTimeText, value); }
        public string NavMapText         { get => _navMapText;         set => SetProperty(ref _navMapText, value); }
        public string NavExpressionText  { get => _navExpressionText;  set => SetProperty(ref _navExpressionText, value); }
        public string NavSystemText      { get => _navSystemText;      set => SetProperty(ref _navSystemText, value); }
        public string NavOtherText       { get => _navOtherText;       set => SetProperty(ref _navOtherText, value); }
        public string NavUpgradeText     { get => _navUpgradeText;     set => SetProperty(ref _navUpgradeText, value); }
        public string NavDeveloperText   { get => _navDeveloperText;   set => SetProperty(ref _navDeveloperText, value); }
        public string RouteWaitLbl       { get => _routeWaitLbl;       set => SetProperty(ref _routeWaitLbl, value); }
        public string RouteWaitDesc      { get => _routeWaitDesc;      set => SetProperty(ref _routeWaitDesc, value); }
        public string RouteSpeedLbl      { get => _routeSpeedLbl;      set => SetProperty(ref _routeSpeedLbl, value); }
        public string RouteSpeedDesc     { get => _routeSpeedDesc;     set => SetProperty(ref _routeSpeedDesc, value); }
        public string SysNetworkTitle    { get => _sysNetworkTitle;    set => SetProperty(ref _sysNetworkTitle, value); }
        public string SysSsidLbl         { get => _sysSsidLbl;         set => SetProperty(ref _sysSsidLbl, value); }
        public string SysMacHeadLbl      { get => _sysMacHeadLbl;      set => SetProperty(ref _sysMacHeadLbl, value); }
        public string SysIpHeadLbl       { get => _sysIpHeadLbl;       set => SetProperty(ref _sysIpHeadLbl, value); }
        public string SysMacWlanLbl      { get => _sysMacWlanLbl;      set => SetProperty(ref _sysMacWlanLbl, value); }
        public string SysIpWlanLbl       { get => _sysIpWlanLbl;       set => SetProperty(ref _sysIpWlanLbl, value); }
        public string SysMacChassisLbl   { get => _sysMacChassisLbl;   set => SetProperty(ref _sysMacChassisLbl, value); }
        public string SysImeiLbl         { get => _sysImeiLbl;         set => SetProperty(ref _sysImeiLbl, value); }
        public string SysFactoryTitle    { get => _sysFactoryTitle;    set => SetProperty(ref _sysFactoryTitle, value); }
        public string SysFactoryDesc     { get => _sysFactoryDesc;     set => SetProperty(ref _sysFactoryDesc, value); }
        public string SysFactoryBtn      { get => _sysFactoryBtn;      set => SetProperty(ref _sysFactoryBtn, value); }
        public string ComingSoonText     { get => _comingSoonText;      set => SetProperty(ref _comingSoonText, value); }
        public string LanguageLabel      { get => _languageLabel;       set => SetProperty(ref _languageLabel, value); }
        // Sound
        public string SoundToggleLbl      { get => _soundToggleLbl;      set => SetProperty(ref _soundToggleLbl, value); }
        public string SoundOnText         { get => _soundOnText;         set => SetProperty(ref _soundOnText, value); }
        public string SoundOffText        { get => _soundOffText;        set => SetProperty(ref _soundOffText, value); }
        public string SoundVolumeLbl      { get => _soundVolumeLbl;      set => SetProperty(ref _soundVolumeLbl, value); }
        public string SoundMusicLbl       { get => _soundMusicLbl;       set => SetProperty(ref _soundMusicLbl, value); }
        public string SoundSpeechLbl      { get => _soundSpeechLbl;      set => SetProperty(ref _soundSpeechLbl, value); }
        public string SoundObstacleLbl    { get => _soundObstacleLbl;    set => SetProperty(ref _soundObstacleLbl, value); }
        public string SoundChooseMusicLbl { get => _soundChooseMusicLbl; set => SetProperty(ref _soundChooseMusicLbl, value); }
        // Basic
        public string BasicTitle            { get => _basicTitle;            set => SetProperty(ref _basicTitle, value); }
        public string BasicModeFast         { get => _basicModeFast;         set => SetProperty(ref _basicModeFast, value); }
        public string BasicModeMulti        { get => _basicModeMulti;        set => SetProperty(ref _basicModeMulti, value); }
        public string BasicModeDirect       { get => _basicModeDirect;       set => SetProperty(ref _basicModeDirect, value); }
        public string BasicModeRoute        { get => _basicModeRoute;        set => SetProperty(ref _basicModeRoute, value); }
        public string BasicModeCustom       { get => _basicModeCustom;       set => SetProperty(ref _basicModeCustom, value); }
        public string BasicDeliveryModeLbl  { get => _basicDeliveryModeLbl;  set => SetProperty(ref _basicDeliveryModeLbl, value); }
        public string BasicDeliveryModeDesc { get => _basicDeliveryModeDesc; set => SetProperty(ref _basicDeliveryModeDesc, value); }
        public string BasicObstacleModeLbl  { get => _basicObstacleModeLbl;  set => SetProperty(ref _basicObstacleModeLbl, value); }
        public string BasicObstacleModeDesc { get => _basicObstacleModeDesc; set => SetProperty(ref _basicObstacleModeDesc, value); }
        public string BasicAutoReturnLbl    { get => _basicAutoReturnLbl;    set => SetProperty(ref _basicAutoReturnLbl, value); }
        public string BasicHomePointLbl     { get => _basicHomePointLbl;     set => SetProperty(ref _basicHomePointLbl, value); }
        public string BasicHomePointDesc    { get => _basicHomePointDesc;    set => SetProperty(ref _basicHomePointDesc, value); }
        public string BasicChargePointLbl   { get => _basicChargePointLbl;   set => SetProperty(ref _basicChargePointLbl, value); }
        public string BasicChargePointDesc  { get => _basicChargePointDesc;  set => SetProperty(ref _basicChargePointDesc, value); }
        // Time
        public string TimeSectionTitle { get => _timeSectionTitle; set => SetProperty(ref _timeSectionTitle, value); }
        public string TimeTabCharging  { get => _timeTabCharging;  set => SetProperty(ref _timeTabCharging, value); }
        public string TimeTabWaiting   { get => _timeTabWaiting;   set => SetProperty(ref _timeTabWaiting, value); }
        public string TimeTabCustom    { get => _timeTabCustom;    set => SetProperty(ref _timeTabCustom, value); }
        public string TimeColTime      { get => _timeColTime;      set => SetProperty(ref _timeColTime, value); }
        public string TimeColName      { get => _timeColName;      set => SetProperty(ref _timeColName, value); }
        public string TimeColType      { get => _timeColType;      set => SetProperty(ref _timeColType, value); }
        public string TimeColNumber    { get => _timeColNumber;    set => SetProperty(ref _timeColNumber, value); }
        public string TimeColRoute     { get => _timeColRoute;     set => SetProperty(ref _timeColRoute, value); }
        public string TimeColRepeat    { get => _timeColRepeat;    set => SetProperty(ref _timeColRepeat, value); }
        public string TimeColStatus    { get => _timeColStatus;    set => SetProperty(ref _timeColStatus, value); }
        public string TimeColAction    { get => _timeColAction;    set => SetProperty(ref _timeColAction, value); }
        public string TimeEditText     { get => _timeEditText;     set => SetProperty(ref _timeEditText, value); }
        public string TimeDeleteText   { get => _timeDeleteText;   set => SetProperty(ref _timeDeleteText, value); }
        public string TimeViewText     { get => _timeViewText;     set => SetProperty(ref _timeViewText, value); }
        // Delivery
        public string DeliveryWaitTimeLbl        { get => _deliveryWaitTimeLbl;        set => SetProperty(ref _deliveryWaitTimeLbl, value); }
        public string DeliveryWaitTimeDesc       { get => _deliveryWaitTimeDesc;       set => SetProperty(ref _deliveryWaitTimeDesc, value); }
        public string DeliverySpeedLbl           { get => _deliverySpeedLbl;           set => SetProperty(ref _deliverySpeedLbl, value); }
        public string DeliverySpeedDesc          { get => _deliverySpeedDesc;          set => SetProperty(ref _deliverySpeedDesc, value); }
        public string DeliveryCollisionDecelLbl  { get => _deliveryCollisionDecelLbl;  set => SetProperty(ref _deliveryCollisionDecelLbl, value); }
        public string DeliveryCollisionDecelDesc { get => _deliveryCollisionDecelDesc; set => SetProperty(ref _deliveryCollisionDecelDesc, value); }
        public string DeliveryRotationSpeedLbl   { get => _deliveryRotationSpeedLbl;   set => SetProperty(ref _deliveryRotationSpeedLbl, value); }
        public string DeliveryRotationSpeedDesc  { get => _deliveryRotationSpeedDesc;  set => SetProperty(ref _deliveryRotationSpeedDesc, value); }
        public string DeliveryWeightLimitLbl     { get => _deliveryWeightLimitLbl;     set => SetProperty(ref _deliveryWeightLimitLbl, value); }
        public string DeliveryReverseLbl         { get => _deliveryReverseLbl;         set => SetProperty(ref _deliveryReverseLbl, value); }
        public string DeliveryReverseDesc        { get => _deliveryReverseDesc;        set => SetProperty(ref _deliveryReverseDesc, value); }
        public string DeliveryVoiceCountdownLbl  { get => _deliveryVoiceCountdownLbl;  set => SetProperty(ref _deliveryVoiceCountdownLbl, value); }
        public string DeliveryVoiceCountdownDesc { get => _deliveryVoiceCountdownDesc; set => SetProperty(ref _deliveryVoiceCountdownDesc, value); }
        // Map
        public string MapTitle { get => _mapTitle; set => SetProperty(ref _mapTitle, value); }
        // System extended
        public string SysPasswordLbl        { get => _sysPasswordLbl;        set => SetProperty(ref _sysPasswordLbl, value); }
        public string SysChangePasswordBtn  { get => _sysChangePasswordBtn;  set => SetProperty(ref _sysChangePasswordBtn, value); }
        public string SysPositioningLbl     { get => _sysPositioningLbl;     set => SetProperty(ref _sysPositioningLbl, value); }
        public string SysPositioningDesc    { get => _sysPositioningDesc;    set => SetProperty(ref _sysPositioningDesc, value); }
        public string SysStartPositioningBtn{ get => _sysStartPositioningBtn;set => SetProperty(ref _sysStartPositioningBtn, value); }
        public string SysInfoTitle          { get => _sysInfoTitle;          set => SetProperty(ref _sysInfoTitle, value); }
        public string SysSerialLbl          { get => _sysSerialLbl;          set => SetProperty(ref _sysSerialLbl, value); }
        public string SysVersionLbl         { get => _sysVersionLbl;         set => SetProperty(ref _sysVersionLbl, value); }
        public string SysCheckUpdateBtn     { get => _sysCheckUpdateBtn;     set => SetProperty(ref _sysCheckUpdateBtn, value); }
        public string SysChassisVersionLbl  { get => _sysChassisVersionLbl;  set => SetProperty(ref _sysChassisVersionLbl, value); }
        public string SysSdkVersionLbl      { get => _sysSdkVersionLbl;      set => SetProperty(ref _sysSdkVersionLbl, value); }
        public string SysFirstActivationLbl { get => _sysFirstActivationLbl; set => SetProperty(ref _sysFirstActivationLbl, value); }
        public string SysNoDataText         { get => _sysNoDataText;         set => SetProperty(ref _sysNoDataText, value); }

#endregion Language

        // ─── Commands ─────────────────────────────────────────────────────────────

        public Command SelectBasicCommand       { get; }
        public Command SelectSoundCommand       { get; }
        public Command SelectVoiceCommand       { get; }
        public Command SelectDeliveryCommand    { get; }
        public Command SelectRouteCommand       { get; }
        public Command SelectTimeCommand        { get; }
        public Command SelectMapCommand         { get; }
        public Command SelectExpressionCommand  { get; }
        public Command SelectSystemCommand      { get; }
        public Command SelectOtherCommand       { get; }
        public Command SelectUpgradeCommand     { get; }
        public Command SelectDeveloperCommand   { get; }
        public Command ToggleLanguageCommand    { get; }
        public Command FactoryResetCommand      { get; }
        public Command ExitCommand              { get; }
        // Basic delivery-mode selection
        public Command SelectFastModeCommand    { get; }
        public Command SelectMultiModeCommand   { get; }
        public Command SelectDirectModeCommand  { get; }
        public Command SelectRouteModeCommand   { get; }
        public Command SelectCustomModeCommand  { get; }
        // Time tab selection
        public Command SelectChargingTabCommand { get; }
        public Command SelectWaitingTabCommand  { get; }
        public Command SelectCustomTabCommand   { get; }

        // ─── Constructor ──────────────────────────────────────────────────────────

        public SetupViewModel(ILocalizationService localization, IMqttService mqtt) : base(localization)
        {
            _mqtt = mqtt;
            SelectBasicCommand      = new Command(() => SelectedSection = SetupSection.Basic);
            SelectSoundCommand      = new Command(() => SelectedSection = SetupSection.Sound);
            SelectVoiceCommand      = new Command(() => SelectedSection = SetupSection.Voice);
            SelectDeliveryCommand   = new Command(() => SelectedSection = SetupSection.Delivery);
            SelectRouteCommand      = new Command(() => SelectedSection = SetupSection.Route);
            SelectTimeCommand       = new Command(() => SelectedSection = SetupSection.Time);
            SelectMapCommand        = new Command(() => SelectedSection = SetupSection.Map);
            SelectExpressionCommand = new Command(() => SelectedSection = SetupSection.Expression);
            SelectSystemCommand     = new Command(() => SelectedSection = SetupSection.System);
            SelectOtherCommand      = new Command(() => SelectedSection = SetupSection.Other);
            SelectUpgradeCommand    = new Command(() => SelectedSection = SetupSection.Upgrade);
            SelectDeveloperCommand  = new Command(() => SelectedSection = SetupSection.Developer);
            ToggleLanguageCommand   = new Command(Localization.ToggleLanguage);
            ExitCommand             = new Command(async () => await Shell.Current.GoToAsync("//main"));

            FactoryResetCommand = new Command(async () =>
            {
                bool confirmed = await Shell.Current.DisplayAlert(
                    SysFactoryTitle, SysFactoryDesc,
                    "OK", StringIds.COMMON_BACK.GetString());
                if (confirmed) { /* TODO: perform factory reset */ }
            });

            SelectFastModeCommand   = new Command(() => SelectedDeliveryModeIndex = 0);
            SelectMultiModeCommand  = new Command(() => SelectedDeliveryModeIndex = 1);
            SelectDirectModeCommand = new Command(() => SelectedDeliveryModeIndex = 2);
            SelectRouteModeCommand  = new Command(() => SelectedDeliveryModeIndex = 3);
            SelectCustomModeCommand = new Command(() => SelectedDeliveryModeIndex = 4);

            SelectChargingTabCommand = new Command(() => SelectedTimeTabIndex = 0);
            SelectWaitingTabCommand  = new Command(() => SelectedTimeTabIndex = 1);
            SelectCustomTabCommand   = new Command(() => SelectedTimeTabIndex = 2);

            RefreshLocalizedProperties();
        }

        private async Task TryConnectMqttForMapAsync()
        {
            try
            {
                if (!_mqtt.IsConnected)
                    await _mqtt.ConnectAsync();
            }
            catch
            {
                // Map still renders; pose line shows waiting until broker connects.
            }
        }

        /// <summary>Subscribe to robot pose while Setup is visible.</summary>
        public void AttachMqttHandlers()
        {
            _mqtt.LocationUpdated += OnLocationUpdated;
        }

        public void DetachMqttHandlers()
        {
            _mqtt.LocationUpdated -= OnLocationUpdated;
        }

        private void OnLocationUpdated(object? sender, LocationModel location)
        {
            MainThread.BeginInvokeOnMainThread(() =>
            {
                RobotMapX = location.X;
                RobotMapY = location.Y;
                RobotMapThetaDegrees = location.Theta;
                _hasMapPose = true;
                RefreshMapPoseSummary();
            });
        }

        private void RefreshMapPoseSummary()
        {
            if (!_hasMapPose)
                MapPoseSummary = StringIds.NAV_MAP_WAITING_POSE.GetString();
            else
                MapPoseSummary = $"X: {RobotMapX:F2}, Y: {RobotMapY:F2}, θ: {RobotMapThetaDegrees:F1}°";
        }

        // ─── Localization ─────────────────────────────────────────────────────────

        protected override void RefreshLocalizedProperties()
        {
            TitleText         = StringIds.SETUP_TITLE.GetString();
            ExitText          = StringIds.SETUP_EXIT.GetString();
            NavBasicText      = StringIds.SETUP_NAV_BASIC.GetString();
            NavSoundText      = StringIds.SETUP_NAV_SOUND.GetString();
            NavVoiceText      = StringIds.SETUP_NAV_VOICE.GetString();
            NavDeliveryText   = StringIds.SETUP_NAV_DELIVERY.GetString();
            NavRouteText      = StringIds.SETUP_NAV_ROUTE.GetString();
            NavTimeText       = StringIds.SETUP_NAV_TIME.GetString();
            NavMapText        = StringIds.SETUP_NAV_MAP.GetString();
            NavExpressionText = StringIds.SETUP_NAV_EXPRESSION.GetString();
            NavSystemText     = StringIds.SETUP_NAV_SYSTEM.GetString();
            NavOtherText      = StringIds.SETUP_NAV_OTHER.GetString();
            NavUpgradeText    = StringIds.SETUP_NAV_UPGRADE.GetString();
            NavDeveloperText  = StringIds.SETUP_NAV_DEVELOPER.GetString();
            RouteWaitLbl      = StringIds.SETUP_ROUTE_WAIT_TIME.GetString();
            RouteWaitDesc     = StringIds.SETUP_ROUTE_WAIT_TIME_DESC.GetString();
            RouteSpeedLbl     = StringIds.SETUP_ROUTE_SPEED.GetString();
            RouteSpeedDesc    = StringIds.SETUP_ROUTE_SPEED_DESC.GetString();
            SysNetworkTitle   = StringIds.SETUP_SYS_NETWORK_INFO.GetString();
            SysSsidLbl        = StringIds.SETUP_SYS_SSID.GetString();
            SysMacHeadLbl     = StringIds.SETUP_SYS_MAC_HEAD.GetString();
            SysIpHeadLbl      = StringIds.SETUP_SYS_IP_HEAD.GetString();
            SysMacWlanLbl     = StringIds.SETUP_SYS_MAC_WLAN.GetString();
            SysIpWlanLbl      = StringIds.SETUP_SYS_IP_WLAN.GetString();
            SysMacChassisLbl  = StringIds.SETUP_SYS_MAC_CHASSIS.GetString();
            SysImeiLbl        = StringIds.SETUP_SYS_IMEI.GetString();
            SysFactoryTitle   = StringIds.SETUP_SYS_FACTORY_RESET.GetString();
            SysFactoryDesc    = StringIds.SETUP_SYS_FACTORY_RESET_DESC.GetString();
            SysFactoryBtn     = StringIds.SETUP_SYS_FACTORY_RESET_BTN.GetString();
            ComingSoonText    = StringIds.SETUP_COMING_SOON.GetString();
            LanguageLabel     = Localization.GetCurrentLanguageName();
            // Sound
            SoundToggleLbl      = StringIds.SETUP_SOUND_TOGGLE.GetString();
            SoundOnText         = StringIds.SETUP_SOUND_ON.GetString();
            SoundOffText        = StringIds.SETUP_SOUND_OFF.GetString();
            SoundVolumeLbl      = StringIds.SETUP_SOUND_VOLUME.GetString();
            SoundMusicLbl       = StringIds.SETUP_SOUND_MUSIC.GetString();
            SoundSpeechLbl      = StringIds.SETUP_SOUND_SPEECH.GetString();
            SoundObstacleLbl    = StringIds.SETUP_SOUND_OBSTACLE.GetString();
            SoundChooseMusicLbl = StringIds.SETUP_SOUND_CHOOSE_MUSIC.GetString();
            // Basic
            BasicTitle            = StringIds.SETUP_BASIC_TITLE.GetString();
            BasicModeFast         = StringIds.SETUP_BASIC_MODE_FAST.GetString();
            BasicModeMulti        = StringIds.SETUP_BASIC_MODE_MULTI.GetString();
            BasicModeDirect       = StringIds.SETUP_BASIC_MODE_DIRECT.GetString();
            BasicModeRoute        = StringIds.SETUP_BASIC_MODE_ROUTE.GetString();
            BasicModeCustom       = StringIds.SETUP_BASIC_MODE_CUSTOM.GetString();
            BasicDeliveryModeLbl  = StringIds.SETUP_BASIC_DELIVERY_MODE.GetString();
            BasicDeliveryModeDesc = StringIds.SETUP_BASIC_DELIVERY_MODE_DESC.GetString();
            BasicObstacleModeLbl  = StringIds.SETUP_BASIC_OBSTACLE_MODE.GetString();
            BasicObstacleModeDesc = StringIds.SETUP_BASIC_OBSTACLE_MODE_DESC.GetString();
            BasicAutoReturnLbl    = StringIds.SETUP_BASIC_AUTO_RETURN.GetString();
            BasicHomePointLbl     = StringIds.SETUP_BASIC_HOME_POINT.GetString();
            BasicHomePointDesc    = StringIds.SETUP_BASIC_HOME_POINT_DESC.GetString();
            BasicChargePointLbl   = StringIds.SETUP_BASIC_CHARGE_POINT.GetString();
            BasicChargePointDesc  = StringIds.SETUP_BASIC_CHARGE_POINT_DESC.GetString();
            UpdateDeliveryModeText();
            // Time
            TimeSectionTitle = StringIds.SETUP_TIME_TITLE.GetString();
            TimeTabCharging  = StringIds.SETUP_TIME_TAB_CHARGING.GetString();
            TimeTabWaiting   = StringIds.SETUP_TIME_TAB_WAITING.GetString();
            TimeTabCustom    = StringIds.SETUP_TIME_TAB_CUSTOM.GetString();
            TimeColTime      = StringIds.SETUP_TIME_COL_TIME.GetString();
            TimeColName      = StringIds.SETUP_TIME_COL_NAME.GetString();
            TimeColType      = StringIds.SETUP_TIME_COL_TYPE.GetString();
            TimeColNumber    = StringIds.SETUP_TIME_COL_NUMBER.GetString();
            TimeColRoute     = StringIds.SETUP_TIME_COL_ROUTE.GetString();
            TimeColRepeat    = StringIds.SETUP_TIME_COL_REPEAT.GetString();
            TimeColStatus    = StringIds.SETUP_TIME_COL_STATUS.GetString();
            TimeColAction    = StringIds.SETUP_TIME_COL_ACTION.GetString();
            TimeEditText     = StringIds.SETUP_TIME_EDIT.GetString();
            TimeDeleteText   = StringIds.SETUP_TIME_DELETE.GetString();
            TimeViewText     = StringIds.SETUP_TIME_VIEW.GetString();
            // Delivery
            DeliveryWaitTimeLbl        = StringIds.SETUP_DELIVERY_WAIT_TIME.GetString();
            DeliveryWaitTimeDesc       = StringIds.SETUP_DELIVERY_WAIT_TIME_DESC.GetString();
            DeliverySpeedLbl           = StringIds.SETUP_DELIVERY_SPEED.GetString();
            DeliverySpeedDesc          = StringIds.SETUP_DELIVERY_SPEED_DESC.GetString();
            DeliveryCollisionDecelLbl  = StringIds.SETUP_DELIVERY_COLLISION_DECEL.GetString();
            DeliveryCollisionDecelDesc = StringIds.SETUP_DELIVERY_COLLISION_DECEL_DESC.GetString();
            DeliveryRotationSpeedLbl   = StringIds.SETUP_DELIVERY_ROTATION_SPEED.GetString();
            DeliveryRotationSpeedDesc  = StringIds.SETUP_DELIVERY_ROTATION_SPEED_DESC.GetString();
            DeliveryWeightLimitLbl     = StringIds.SETUP_DELIVERY_WEIGHT_LIMIT.GetString();
            DeliveryReverseLbl         = StringIds.SETUP_DELIVERY_REVERSE.GetString();
            DeliveryReverseDesc        = StringIds.SETUP_DELIVERY_REVERSE_DESC.GetString();
            DeliveryVoiceCountdownLbl  = StringIds.SETUP_DELIVERY_VOICE_COUNTDOWN.GetString();
            DeliveryVoiceCountdownDesc = StringIds.SETUP_DELIVERY_VOICE_COUNTDOWN_DESC.GetString();
            // Map
            MapTitle = StringIds.SETUP_MAP_TITLE.GetString();
            MapPanHint = StringIds.NAV_MAP_PAN_HINT.GetString();
            RefreshMapPoseSummary();
            // System extended
            SysPasswordLbl         = StringIds.SETUP_SYS_PASSWORD.GetString();
            SysChangePasswordBtn   = StringIds.SETUP_SYS_CHANGE_PASSWORD.GetString();
            SysPositioningLbl      = StringIds.SETUP_SYS_POSITIONING.GetString();
            SysPositioningDesc     = StringIds.SETUP_SYS_POSITIONING_DESC.GetString();
            SysStartPositioningBtn = StringIds.SETUP_SYS_START_POSITIONING.GetString();
            SysInfoTitle           = StringIds.SETUP_SYS_INFO_TITLE.GetString();
            SysSerialLbl           = StringIds.SETUP_SYS_SERIAL_LBL.GetString();
            SysVersionLbl          = StringIds.SETUP_SYS_VERSION_LBL.GetString();
            SysCheckUpdateBtn      = StringIds.SETUP_SYS_CHECK_UPDATE.GetString();
            SysChassisVersionLbl   = StringIds.SETUP_SYS_CHASSIS_VER_LBL.GetString();
            SysSdkVersionLbl       = StringIds.SETUP_SYS_SDK_VER_LBL.GetString();
            SysFirstActivationLbl  = StringIds.SETUP_SYS_FIRST_ACT_LBL.GetString();
            SysNoDataText          = StringIds.SETUP_SYS_NO_DATA.GetString();
        }

        // ─── Helpers ──────────────────────────────────────────────────────────────

        private void NotifySelectionBools()
        {
            OnPropertyChanged(nameof(IsBasicSelected));
            OnPropertyChanged(nameof(IsSoundSelected));
            OnPropertyChanged(nameof(IsVoiceSelected));
            OnPropertyChanged(nameof(IsDeliverySelected));
            OnPropertyChanged(nameof(IsRouteSelected));
            OnPropertyChanged(nameof(IsTimeSelected));
            OnPropertyChanged(nameof(IsMapSelected));
            OnPropertyChanged(nameof(IsExpressionSelected));
            OnPropertyChanged(nameof(IsSystemSelected));
            OnPropertyChanged(nameof(IsOtherSelected));
            OnPropertyChanged(nameof(IsUpgradeSelected));
            OnPropertyChanged(nameof(IsDeveloperSelected));
            OnPropertyChanged(nameof(IsPlaceholderSelected));
        }

        private void NotifyDeliveryModeBools()
        {
            OnPropertyChanged(nameof(IsFastModeSelected));
            OnPropertyChanged(nameof(IsMultiModeSelected));
            OnPropertyChanged(nameof(IsDirectModeSelected));
            OnPropertyChanged(nameof(IsRouteModeSelected));
            OnPropertyChanged(nameof(IsCustomModeSelected));
        }

        private void NotifyTimeTabBools()
        {
            OnPropertyChanged(nameof(IsChargingTabSelected));
            OnPropertyChanged(nameof(IsWaitingTabSelected));
            OnPropertyChanged(nameof(IsCustomTabSelected));
        }

        private void UpdateDeliveryModeText()
        {
            SelectedDeliveryModeText = SelectedDeliveryModeIndex switch
            {
                0 => BasicModeFast,
                1 => BasicModeMulti,
                2 => BasicModeDirect,
                3 => BasicModeRoute,
                4 => BasicModeCustom,
                _ => string.Empty,
            };
        }
    }
}
