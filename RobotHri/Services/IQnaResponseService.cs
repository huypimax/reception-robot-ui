namespace RobotHri.Services
{
    public interface IQnaResponseService
    {
        Task<string> GetAnswerAsync(string query, string languageCode, CancellationToken cancellationToken = default);
    }
}
