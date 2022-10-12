
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

        [Inject]
        protected IOptions<FACEAPI> FaceOptions { get; set; }

        public string Status { get; set; }

        IFaceClient _client;
        public static IFaceClient Authenticate(string endpoint, string key)
        {
            return new FaceClient(new ApiKeyServiceClientCredentials(key)) { Endpoint = endpoint };
        }
        //find similar faces from Azure FaceAPI
        private async Task<IList<SimilarFace>> getSimilarFaces(string faceId1, string faceId2)
        {
            IList<SimilarFace> similarResults = await _client.Face.FindSimilarAsync(new Guid(faceId1), null, null, new List<Guid?>{ new Guid(faceId2)});
            return similarResults;
        }

        
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

        protected IEnumerable<FaceResult> getImagesFromDirAsBase64()
        {
            foreach (var face in getImagesFromDir())
            {
                Encoding iso = Encoding.GetEncoding("ISO-8859-1");
                getSimilarFaces(face.face_id,"ce4c7425-e289-4c2a-bf67-54d5d86cc7c4").GetAwaiter().GetResult();
                var result = face.img;
                yield return new FaceResult { Base64Src = "data:image/png;base64," + result, Gender = $"{face.gender}", Extra = face.gender };
            }
        }

        protected override void OnInitialized()
        {
            if (Config != null) {

        var c = Config.GetSection("FACEAPI").Value;

        Console.WriteLine(c);
    }
            //Console.WriteLine(FaceOptions.ENDPOINT);
            //Status = "OnInitialized";   
            //const string RECOGNITION_MODEL4 = RecognitionModel.Recognition04;
//
            //// Authenticate.
            //_client = Authenticate(FaceOptions.ENDPOINT, FaceOptions.KEY);
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