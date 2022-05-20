using Microsoft.AspNetCore.Mvc;
using ProgressiveWebApp.Shared;
using StackExchange.Redis;
using System.Text.Json;
using WebPush;

namespace ProgressiveWebApp.Server.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class NotificationsController : ControllerBase
    {
        private IConnectionMultiplexer? _cnnMulti;

        public NotificationsController(IConnectionMultiplexer? cnnMulti)
        {
            _cnnMulti = cnnMulti;
        }

        [HttpPut("subscribe")]
        public async Task<NotificationSubscription> Subscribe(NotificationSubscription subscription)
        {
            var redisDb = _cnnMulti.GetDatabase(0);

            // We're storing at most one subscription per user, so delete old ones.
            // Alternatively, you could let the user register multiple subscriptions from different browsers/devices.
            try
            {
                var result = await redisDb.StringGetDeleteAsync(subscription.UserId);
            }
            catch (Exception)
            {
                // Nothing in here
            }

            // Store new subscription
            var subscriptionJson = JsonSerializer.Serialize(subscription);
            await redisDb.StringSetAsync(subscription.UserId, subscriptionJson);

            return subscription;
        }

        [HttpGet]
        [Route("NotifyMe/{userId}")]
        public async Task NotifyUser(string userId)
        {
            var redisDb = _cnnMulti.GetDatabase(0);
            var subscriptionJson = await redisDb.StringGetAsync(userId);
            var subscription = JsonSerializer.Deserialize<NotificationSubscription>(subscriptionJson);

            // For a real application, generate your own
            var publicKey = "BLC8GOevpcpjQiLkO7JmVClQjycvTCYWm6Cq_a7wJZlstGTVZvwGFFHMYfXt6Njyvgx_GlXJeo5cSiZ1y4JOx1o";
            var privateKey = "OrubzSz3yWACscZXjFQrrtDwCKg-TGFuWhluQ2wLXDo";

            var pushSubscription = new PushSubscription(subscription.Url, subscription.P256dh, subscription.Auth);
            var vapidDetails = new VapidDetails("mailto:<someone@example.com>", publicKey, privateKey);
            var webPushClient = new WebPushClient();

            string message = "Hello World!";
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
}
