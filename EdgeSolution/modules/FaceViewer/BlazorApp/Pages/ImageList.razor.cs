
using System.Text;
using System;
using System.Text.Json;
using BlazorApp.Data;
using Microsoft.AspNetCore.Components;
using StackExchange.Redis;
using Microsoft.Azure.CognitiveServices;
using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;
using Microsoft.Extensions.Options;
using BlazorApp.Data;

namespace BlazorApp.Pages
{
    public partial class ImageList
    {
        private IConnectionMultiplexer? _cnnMulti;
        [Inject]
        protected IConnectionMultiplexer CnnMulti { get => _cnnMulti; set => _cnnMulti = value; }

        [Inject]
        protected IConfiguration Config { get; set; }

        public string Status { get; set; }

        private HalloweenFaces _halloweenFaces;

        public List<FaceResult> images = new List<FaceResult>();
        List<RedisRecord> _inmemoryRedisFaces;

        protected IEnumerable<RedisRecord> getImagesFromDir()
        {
            var servers = CnnMulti.GetEndPoints();
            if (servers.Any())
            {
                var server = servers.First();

                var instance = CnnMulti.GetServer(server);

                foreach (var key in instance.Keys(0, "*"))
                {
                    string result = "";
                    var redisDb = CnnMulti.GetDatabase(0);
                    var record = redisDb.HashGetAll(key);
                    var jsonResult = JsonSerializer.Deserialize<RedisRecord>(record[0].Value);

                    yield return jsonResult;
                }
            }
        }

        protected async IAsyncEnumerable<FaceResult> getImagesFromDirAsBase64()
        {
            foreach (var group in _halloweenFaces.Groups)
            {
                foreach (var item in group)
                {
                    var face = _inmemoryRedisFaces.Where(x => x.face_id == item.ToString()).FirstOrDefault();
                    if (face != null)
                    {
                        var result = face.img;
                        yield return new FaceResult { Base64Src = "data:image/png;base64," + result, Gender = $"{face.gender}", Extra = face.gender };
                    }
                }
            }
        }

        private async Task<List<RedisRecord>> LoadRedisFaces()
        {
            List<RedisRecord> inmemoryRedisFaces = new List<RedisRecord>();
            foreach (var face in getImagesFromDir())
            {
                Encoding iso = Encoding.GetEncoding("ISO-8859-1");
                var resultInvalid = await _halloweenFaces.AddFaceAndGroup(face);
                inmemoryRedisFaces.Add(face);
            }

            return inmemoryRedisFaces;
        }

        protected override async Task OnInitializedAsync()
        {
            Status = "OnInitialized";

            _halloweenFaces = new HalloweenFaces(this.Config);
            await _halloweenFaces.Init();
            await _halloweenFaces.RecreateFaceList();
            _inmemoryRedisFaces = await LoadRedisFaces();

            var throttledStateHasChanged = Throttle(
                        () => InvokeAsync(StateHasChanged),
                        TimeSpan.FromMilliseconds(500));

            images = new List<FaceResult>();
            await foreach (var image in getImagesFromDirAsBase64())
            {
                images.Add(image);
                throttledStateHasChanged();
            }
        }

        // https://www.meziantou.net/debouncing-throttling-javascript-events-in-a-blazor-application.htm#throttle-debounce-on
        private static Action Throttle(Action action, TimeSpan interval)
        {
            Task task = null;
            var l = new object();
            return () =>
            {
                if (task != null)
                    return;

                lock (l)
                {
                    if (task != null)
                        return;

                    task = Task.Delay(interval).ContinueWith(t =>
                    {
                        action();
                        task = null;
                    });
                }
            };
        }

        protected void onClickDelete()
        {
            this.Status = "";

            {
                var servers = CnnMulti.GetEndPoints();
                if (servers.Any())
                {
                    var server = servers.First();

                    var instance = CnnMulti.GetServer(server);

                    foreach (var key in instance.Keys(0, "*"))
                    {
                        var redisDb = CnnMulti.GetDatabase(0);
                        var deleted = redisDb.KeyDelete(key);
                        if (!deleted)
                        {
                            System.Diagnostics.Debug.WriteLine($"Error deleting key {key}");
                            this.Status = $"Error deleting image {key}";
                        }
                    }
                }
            }
        }

    }
}