using MQTTnet;
using MQTTnet.Client;
using RobotHri.Constants;
using RobotHri.Models;
using System.Text;
using System.Text.Json;

namespace RobotHri.Services
{
    /// <summary>
    /// Manages MQTT connection to robot broker.
    /// Mirrors mqtt_manager.py + publish_goal.py + subscribe_arrival.py.
    /// </summary>
    public class MqttService : IMqttService, IDisposable
    {
        private IMqttClient? _client;
        private readonly MqttFactory _factory = new MqttFactory();

        public bool IsConnected => _client?.IsConnected ?? false;

        public event EventHandler<bool>? ArrivalReceived;
        public event EventHandler<LocationModel>? LocationUpdated;

        public async Task<bool> ConnectAsync()
        {
            try
            {
                _client = _factory.CreateMqttClient();
                _client.ApplicationMessageReceivedAsync += OnMessageReceived;

                var options = new MqttClientOptionsBuilder()
                    .WithTcpServer(MqttConstants.BrokerHost, MqttConstants.BrokerPort)
                    .WithCredentials(MqttConstants.ClientId, MqttConstants.Password)
                    .WithCleanSession()
                    .Build();

                await _client.ConnectAsync(options);

                // Subscribe to topics
                await _client.SubscribeAsync(MqttConstants.TopicArrival);
                await _client.SubscribeAsync(MqttConstants.TopicLocation);

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[MQTT] Connect failed: {ex.Message}");
                return false;
            }
        }

        public async Task DisconnectAsync()
        {
            if (_client?.IsConnected == true)
                await _client.DisconnectAsync();
        }

        public async Task PublishGoalAsync(string destination)
        {
            if (!IsConnected) return;
            var payload = JsonSerializer.Serialize(new { destination });
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(MqttConstants.TopicGoal)
                .WithPayload(Encoding.UTF8.GetBytes(payload))
                .Build();
            await _client!.PublishAsync(message);
        }

        public async Task PublishWaypointsAsync(IEnumerable<LocationModel> waypoints)
        {
            if (!IsConnected) return;
            var payload = JsonSerializer.Serialize(waypoints);
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(MqttConstants.TopicWaypoints)
                .WithPayload(Encoding.UTF8.GetBytes(payload))
                .Build();
            await _client!.PublishAsync(message);
        }

        private Task OnMessageReceived(MqttApplicationMessageReceivedEventArgs e)
        {
            var topic = e.ApplicationMessage.Topic;
            var payload = Encoding.UTF8.GetString(e.ApplicationMessage.PayloadSegment);

            if (topic == MqttConstants.TopicArrival)
            {
                bool arrived = payload.Trim('"').Equals("true", StringComparison.OrdinalIgnoreCase);
                MainThread.BeginInvokeOnMainThread(() => ArrivalReceived?.Invoke(this, arrived));
            }
            else if (topic == MqttConstants.TopicLocation)
            {
                try
                {
                    var location = JsonSerializer.Deserialize<LocationModel>(payload);
                    if (location != null)
                        MainThread.BeginInvokeOnMainThread(() => LocationUpdated?.Invoke(this, location));
                }
                catch { }
            }

            return Task.CompletedTask;
        }

        public void Dispose()
        {
            _client?.Dispose();
        }
    }
}
