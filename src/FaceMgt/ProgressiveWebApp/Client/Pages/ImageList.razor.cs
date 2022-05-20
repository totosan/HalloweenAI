using Microsoft.AspNetCore.Components;
using ProgressiveWebApp.Shared;
using System.Net.Http.Json;

namespace ProgressiveWebApp.Client.Pages
{
    public partial class ImageList : ComponentBase
    {
        [Inject]
        protected HttpClient Http { get; set; }
        public string Status { get; set; }
        public IEnumerable<FaceResult> Images { get; set; } = new List<FaceResult>();

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

    }
}
