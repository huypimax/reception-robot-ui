using CommunityToolkit.Maui;
using Plugin.Maui.Audio;
using Microsoft.Extensions.Logging;
using RobotHri.Services;
using RobotHri.ViewModels;
using RobotHri.Views;
using SkiaSharp.Views.Maui.Controls.Hosting;

namespace RobotHri
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();

            builder
                .UseMauiApp<App>()
                .UseSkiaSharp()
                .UseMauiCommunityToolkit()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");

                    // Roboto aliases — replace with Roboto-Regular.ttf / Roboto-Bold.ttf
                    // when you add those files to Resources/Fonts/
                    fonts.AddFont("OpenSans-Regular.ttf", "RobotoRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "RobotoBold");
                });

            // ── Services ──────────────────────────────────────────
            builder.Services.AddSingleton<ILocalizationService, LocalizationService>();
            builder.Services.AddSingleton<IMqttService, MqttService>();
            builder.Services.AddSingleton<CommunityToolkit.Maui.Media.ISpeechToText>(
                CommunityToolkit.Maui.Media.SpeechToText.Default);
            builder.Services.AddSingleton<IAudioManager>(AudioManager.Current);
            builder.Services.AddSingleton<ISpeechService, SpeechService>();

            // ── ViewModels ────────────────────────────────────────
            builder.Services.AddTransient<MainViewModel>();
            builder.Services.AddTransient<QnaViewModel>();
            builder.Services.AddTransient<NaviViewModel>();
            builder.Services.AddTransient<LabViewModel>();
            builder.Services.AddTransient<DeliViewModel>();
            builder.Services.AddTransient<SetupViewModel>();

            // ── Views / Pages ─────────────────────────────────────
            builder.Services.AddTransient<MainPage>();
            builder.Services.AddTransient<QnaPage>();
            builder.Services.AddTransient<NaviPage>();
            builder.Services.AddTransient<LabPage>();
            builder.Services.AddTransient<DeliPage>();
            builder.Services.AddTransient<SetupPage>();

#if DEBUG
            builder.Logging.AddDebug();
#endif

            return builder.Build();
        }
    }
}
