using Microsoft.AspNetCore.Mvc;
using ProgressiveWebApp.Shared;
using StackExchange.Redis;
using System.Text;
using System.Text.Json;

namespace ProgressiveWebApp.Server.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ImageListController : ControllerBase
    {
        private IConnectionMultiplexer? _cnnMulti;

        public ImageListController(IConnectionMultiplexer cnnMulti)
        {
            _cnnMulti = cnnMulti;
        }

        public IActionResult Index()
        {
            var images = GetImagesFromDir();

            return Ok(images);
        }

        [HttpDelete]
        public IActionResult DeleteAll()
        {
            var servers = _cnnMulti.GetEndPoints();
            if (servers.Any())
            {
                var server = servers.First();

                var instance = _cnnMulti.GetServer(server);

                foreach (var key in instance.Keys(0, "face*"))
                {
                    var redisDb = _cnnMulti.GetDatabase(0);
                    var deleted = redisDb.KeyDelete(key);
                    if (!deleted)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error deleting key {key}");
                        return BadRequest(key);
                    }
                }
            }

            return Accepted();
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
