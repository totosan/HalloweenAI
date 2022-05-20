
using ProgressiveWebApp.Shared;
using StackExchange.Redis;
using System.Text;
using System.Text.Json;
using WebPush;

namespace ProgressiveWebApp.Server
{
    public class NotificationBackgroundService : IHostedService, IDisposable
    {
        private int facesCount = 0;
        private Timer _timer = null!;
        private IConnectionMultiplexer? _cnnMulti;
        private readonly ILogger<BackgroundService> _logger;

        public NotificationBackgroundService(IConnectionMultiplexer? cnnMulti, ILogger<BackgroundService> logger)
        {
            _cnnMulti = cnnMulti;
            _logger = logger;
        }

        public void Dispose()
        {
            _timer?.Dispose();
        }

        public Task StartAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Timed Hosted Service running.");

            _timer = new Timer(DoWork, null, TimeSpan.Zero,
                TimeSpan.FromSeconds(30));

            return Task.CompletedTask;
        }

        private void DoWork(object? state)
        {
            SendNotificationAsync();
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Timed Hosted Service is stopping.");

            _timer?.Change(Timeout.Infinite, 0);

            return Task.CompletedTask;
        }

        private async Task SendNotificationAsync()
        {
            var redisDb = _cnnMulti.GetDatabase(0);
            var subscriptionJson = await redisDb.StringGetAsync("Niels");
            var subscription = JsonSerializer.Deserialize<NotificationSubscription>(subscriptionJson);

            // For a real application, generate your own
            var publicKey = "BLC8GOevpcpjQiLkO7JmVClQjycvTCYWm6Cq_a7wJZlstGTVZvwGFFHMYfXt6Njyvgx_GlXJeo5cSiZ1y4JOx1o";
            var privateKey = "OrubzSz3yWACscZXjFQrrtDwCKg-TGFuWhluQ2wLXDo";

            var pushSubscription = new PushSubscription(subscription.Url, subscription.P256dh, subscription.Auth);
            var vapidDetails = new VapidDetails("mailto:<someone@example.com>", publicKey, privateKey);
            var webPushClient = new WebPushClient();

            var faces = GetImagesFromDir();
            var retrievedFaces = faces.ToList();

            if (facesCount < retrievedFaces.Count)
            {
                var newFacesCount = faces.Count() - facesCount;
                facesCount += newFacesCount;

                string message = $"Face recognition found {newFacesCount} new faces";
                string url = "https://localhost:7108/images";
                try
                {
                    var payload = JsonSerializer.Serialize(new
                    {
                        message,
                        url = url,
                    });
                    await webPushClient.SendNotificationAsync(pushSubscription, payload, vapidDetails);
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine("Error sending push notification: " + ex.Message);
                }
            }
        }

        private IEnumerable<FaceResult> GetImagesFromDir()
        {
            var servers = _cnnMulti.GetEndPoints();
            if (servers.Any())
            {
                var server = servers.First();

                var instance = _cnnMulti.GetServer(server);

                foreach (var key in instance.Keys(0, "face*"))
                {
                    string result = "";
                    var redisDb = _cnnMulti.GetDatabase(0);
                    var record = redisDb.HashGetAll(key);
                    var jsonResult = JsonSerializer.Deserialize<RedisRecord>(record[1].Value);

                    Encoding iso = Encoding.GetEncoding("ISO-8859-1");
                    result = jsonResult.img;
                    yield return new FaceResult { Base64Src = "data:image/png;base64," + result, Gender = $"{jsonResult.gender}", Extra = jsonResult.gender };
                }
            }
        }
    }
}
