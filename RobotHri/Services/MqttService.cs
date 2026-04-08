using MQTTnet;
using MQTTnet.Client;
using RobotHri.Constants;
using RobotHri.Models;
using System.Diagnostics;
using System.Text;
using System.Text.Json;

namespace RobotHri.Services
{
    public class MqttService : IMqttService, IDisposable
    {
        private IMqttClient? _client;
        private readonly MqttFactory _factory = new MqttFactory();

        public bool IsConnected => _client?.IsConnected ?? false;

        public event EventHandler<bool>? ArrivalReceived;
        public event EventHandler<LocationModel>? LocationUpdated;

        public async Task<bool> ConnectAsync()
        {
            if (IsConnected)
            {
                Debug.WriteLine("[MQTT] Already connected.");
                return true;
            }

            Debug.WriteLine("[MQTT] Attempting to connect...");
            try
            {
                _client = _factory.CreateMqttClient();
                _client.ApplicationMessageReceivedAsync += OnMessageReceived;
                _client.ConnectedAsync += e => {
                    Debug.WriteLine("[MQTT] Connected successfully to broker.");
                    return Task.CompletedTask;
                };
                _client.DisconnectedAsync += e => {
                    Debug.WriteLine("[MQTT] Disconnected from broker.");
                    return Task.CompletedTask;
                };

                var options = new MqttClientOptionsBuilder()
                    .WithTcpServer(MqttConstants.BrokerHost, MqttConstants.BrokerPort)
                    .WithCredentials(MqttConstants.ClientId, MqttConstants.Password)
                    .WithCleanSession()
                    .Build();

                await _client.ConnectAsync(options);

                Debug.WriteLine($"[MQTT] Subscribing to topic: {MqttConstants.TopicArrival}");
                await _client.SubscribeAsync(MqttConstants.TopicArrival);

                Debug.WriteLine($"[MQTT] Subscribing to topic: {MqttConstants.TopicLocation}");
                await _client.SubscribeAsync(MqttConstants.TopicLocation);

                return true;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[MQTT] Connect failed: {ex.Message}");
                return false;
            }
        }

        public async Task DisconnectAsync()
        {
            if (_client?.IsConnected == true)
            {
                Debug.WriteLine("[MQTT] Attempting to disconnect...");
                await _client.DisconnectAsync();
            }
        }

        public async Task PublishGoalAsync(string destination)
        {
            if (!IsConnected)
            {
                Debug.WriteLine("[MQTT] Cannot publish goal, not connected.");
                return;
            }
            //var payload = JsonSerializer.Serialize(new { destination });
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(MqttConstants.TopicGoal)
                .WithPayload(Encoding.UTF8.GetBytes($"\"{destination}\""))
                .Build();

            Debug.WriteLine($"[MQTT] Publishing to '{MqttConstants.TopicGoal}': {destination}");
            await _client!.PublishAsync(message);
        }

        public async Task PublishWaypointsAsync(IEnumerable<LocationModel> waypoints)
        {
            if (!IsConnected)
            {
                Debug.WriteLine("[MQTT] Cannot publish waypoints, not connected.");
                return;
            }
            var payload = JsonSerializer.Serialize(waypoints);
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(MqttConstants.TopicWaypoints)
                .WithPayload(Encoding.UTF8.GetBytes(payload))
                .Build();

            Debug.WriteLine($"[MQTT] Publishing to '{MqttConstants.TopicWaypoints}': {payload}");
            await _client!.PublishAsync(message);
        }

        public async Task PublishSpeedSettingsAsync(double normalSpeed, double rotationSpeed, double roughTerrainSpeed)
        {
            if (!IsConnected)
            {
                Debug.WriteLine("[MQTT] Cannot publish speed settings, not connected.");
                return;
            }

            var payloadObj = new
            {
                normal_speed = normalSpeed,
                rotation_speed = rotationSpeed,
                rough_terrain_speed = roughTerrainSpeed
            };
            var payload = JsonSerializer.Serialize(payloadObj);
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(MqttConstants.TopicSpeedConfig)
                .WithPayload(Encoding.UTF8.GetBytes(payload))
                .Build();

            Debug.WriteLine($"[MQTT] Publishing to '{MqttConstants.TopicSpeedConfig}': {payload}");
            await _client!.PublishAsync(message);
        }

        private Task OnMessageReceived(MqttApplicationMessageReceivedEventArgs e)
        {
            var topic = e.ApplicationMessage.Topic;
            var payload = Encoding.UTF8.GetString(e.ApplicationMessage.PayloadSegment);

            Debug.WriteLine($"[MQTT] Received message on topic '{topic}': {payload}");

            if (topic == MqttConstants.TopicArrival)
            {
                bool arrived = payload.Trim('"').Equals("true", StringComparison.OrdinalIgnoreCase);
                Debug.WriteLine($"[MQTT] Parsed arrival as: {arrived}");
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
                catch (Exception ex)
                {
                    Debug.WriteLine($"[MQTT] Failed to deserialize location payload: {ex.Message}");
                }
            }

            return Task.CompletedTask;
        }

        public void Dispose()
        {
            _client?.Dispose();
        }
    }
}
