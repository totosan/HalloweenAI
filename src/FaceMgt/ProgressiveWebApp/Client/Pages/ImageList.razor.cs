using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using ProgressiveWebApp.Shared;
using System.Net.Http.Json;

namespace ProgressiveWebApp.Client.Pages
{
    public partial class ImageList : ComponentBase
    {
        [Inject]
        protected HttpClient Http { get; set; }
        [Inject]
        protected IJSRuntime JSRuntime { get; set; }
        public string Status { get; set; }
        public IEnumerable<FaceResult> Images { get; set; } = new List<FaceResult>();

        protected override void OnInitialized()
        {
            // In the background, ask if they want to be notified about order updates
            _ = RequestNotificationSubscriptionAsync();
        }

        protected override async Task OnInitializedAsync()
        {
            if (!Images.Any())
            {
                var result = await Http.GetFromJsonAsync<IEnumerable<FaceResult>>("ImageList");
                if (result != null)
                {
                    Images = result; 
                }
            }
        }

        async Task RequestNotificationSubscriptionAsync()
        {
            try
            {
                var subscription = await JSRuntime.InvokeAsync<NotificationSubscription>("blazorPushNotifications.requestSubscription");
                if (subscription != null)
                {
                    try
                    {
                        // TODO: UserId determination
                        subscription.UserId = "Niels";
                        await SubscribeToNotifications(subscription);
                    }
                    catch (Exception ex)
                    {
                        // Do something
                    }
                }
            }
            catch (Exception ex)
            {

                throw;
            }
        }

        protected async Task onClickDelete()
        {
            Status = "";

            var result = await Http.DeleteAsync("ImageList");

            if (!result.IsSuccessStatusCode)
            {
                var message = await result.Content.ReadAsStringAsync();
                Status = $"Error deleting image {message}";
            }
        }

        protected async Task onNotifyMe()
        {
            var response = await Http.GetAsync("Notifications/NotifyMe/Niels");
            response.EnsureSuccessStatusCode();
        }

        private async Task SubscribeToNotifications(NotificationSubscription subscription)
        {
            var response = await Http.PutAsJsonAsync("Notifications/subscribe", subscription);
            response.EnsureSuccessStatusCode();
        }
    }
}
