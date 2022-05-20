using Microsoft.AspNetCore.Components;
using ProgressiveWebApp.Shared;
using SimpleDragAndDropWithBlazor.Models;
using System.Net.Http.Json;

namespace ProgressiveWebApp.Client.Pages
{
    public partial class ImageList : ComponentBase
    {
        [Inject]
        protected HttpClient Http { get; set; }
        public string Status { get; set; }
        public IEnumerable<FaceResult> Images { get; set; } = new List<FaceResult>();
        public List<JobModel> Jobs { get; set; }

        protected override async Task OnInitializedAsync()
        {
            if (!Images.Any())
            {
                var results = await Http.GetFromJsonAsync<IEnumerable<FaceResult>>("ImageList");
                if (results == null)
                {
                    return;
                }

                foreach(var result in results)
                {
                    Jobs.Add(new JobModel{
                        base64Picture = result.Base64Src,
                        Status = (JobStatuses)Enum.Parse(typeof(JobStatuses), result.Status)
                    });
                }

            }

            JobModel test = new();
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
