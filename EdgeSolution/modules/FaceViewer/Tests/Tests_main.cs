using Microsoft.Extensions.Configuration;
using System.Text.Json;

partial class Tests
{
    RedisRecord? redisFace;
    private IConfiguration _config;
    private HalloweenFaces _faces;

    public Tests(IConfiguration configuration)
    {
        //read redisrecord from json file
        redisFace = JsonSerializer.Deserialize<RedisRecord>(File.ReadAllText("RedisRecordFace.json"));
        _config = configuration;
        _faces = new HalloweenFaces(_config);

    }

    public void TestCleanup(){
        _faces.InitFaceList().Wait();
    }
}