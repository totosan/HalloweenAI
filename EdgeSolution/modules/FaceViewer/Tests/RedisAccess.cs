using Microsoft.Extensions.Configuration;
using StackExchange.Redis;
using System.Text.Json;
public class RedisAccess
{
    IConnectionMultiplexer CnnMulti;

    public RedisAccess(IConfiguration config)
    {
        var redis_cnn = config["REDIS_CONN_STR"];
        var redis_key = config["REDIS_KEY"];
        var redis_port = config["Redis:REDIS_PORT"];

        // write all redis vars out
        Console.WriteLine($"{redis_cnn}:{redis_port} with key {redis_key}");

        CnnMulti = ConnectionMultiplexer.Connect(
        new ConfigurationOptions
        {
            EndPoints = { $"{redis_cnn}:{redis_port}" },
            AbortOnConnectFail = true,
            Password = redis_key,
            Ssl = true
        });
    }

    protected IEnumerable<RedisRecord> getImagesFromDir()
    {
        var servers = CnnMulti.GetEndPoints();
        if (servers.Any())
        {
            var server = servers.First();

            var instance = CnnMulti.GetServer(server);
            var redisDb = CnnMulti.GetDatabase(0);

            foreach (var key in instance.Keys(0, "*"))
            {
                string result = "";
                var record = redisDb.HashGetAll(key);
                var jsonResult = JsonSerializer.Deserialize<RedisRecord>(record[0].Value);

                yield return jsonResult;
            }
        }
    }

    public IEnumerable<RedisRecord> GetImages()
    {
        return getImagesFromDir();
    }

    public void SaveImage(RedisRecord record)
    {
        var json = JsonSerializer.Serialize(record);
        var key = $"{record.face_id}";
        SaveJson("faces:images", key, json);
    }

    public void SaveJson(string hashName, string key, string json)
    {
        var servers = CnnMulti.GetEndPoints();
        if (servers.Any())
        {
            var server = servers.First();

            var instance = CnnMulti.GetServer(server);
            var redisDb = CnnMulti.GetDatabase(0);

            var hash = new HashEntry[] { new HashEntry(hashName, json) };

            redisDb.HashSet(key, hash);
        }
    }

    public void DeleteAll()
    {
        var servers = CnnMulti.GetEndPoints();
        if (servers.Any())
        {
            var server = servers.First();
            var instance = CnnMulti.GetServer(server);
            var redisDb = CnnMulti.GetDatabase(0);
            foreach (var key in instance.Keys(0, "*"))
            {
                redisDb.KeyDelete(key);
            }
        }
    }
}