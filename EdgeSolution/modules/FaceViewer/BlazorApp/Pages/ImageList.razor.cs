
using System.Text;
using System.Text.Json;
using BlazorApp.Data;
using Microsoft.AspNetCore.Components;
using StackExchange.Redis;
using Microsoft.Azure.CognitiveServices;

namespace BlazorApp.Pages
{
    public partial class ImageList
    {
        private IConnectionMultiplexer? _cnnMulti;
        [Inject]
        protected IConnectionMultiplexer CnnMulti { get => _cnnMulti; set => _cnnMulti = value; }
        public string Status { get; set; }
        protected IEnumerable<FaceResult> getImagesFromDir()
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

                    Encoding iso = Encoding.GetEncoding("ISO-8859-1");
                    result = jsonResult.img;
                    yield return new FaceResult { Base64Src = "data:image/png;base64," + result, Gender = $"{jsonResult.gender}", Extra = jsonResult.gender };
                }
            }
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