using System.Globalization;

namespace RobotHri.ViewModels
{
    /// <summary>
    /// Inverts a boolean binding: True → False, False → True.
    /// </summary>
    public class InverseBoolConverter : IValueConverter
    {
        public static readonly InverseBoolConverter Instance = new();

        public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
            => value is bool b ? !b : value!;

        public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
            => value is bool b ? !b : value!;
    }

    /// <summary>
    /// Returns true when the bound value equals the converter parameter.
    /// Used to highlight the active nav room button.
    /// </summary>
    public class EqualityConverter : IValueConverter
    {
        public static readonly EqualityConverter Instance = new();

        public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
            => Equals(value?.ToString(), parameter?.ToString());

        public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}
