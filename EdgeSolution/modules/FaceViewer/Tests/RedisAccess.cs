using StackExchange.Redis;
using System.Text.Json;
public class RedisAccess
{
    IConnectionMultiplexer CnnMulti;

    public RedisAccess()
    {
        var redis_cnn = Environment.GetEnvironmentVariable("REDIS_CONN");
        var redis_key = Environment.GetEnvironmentVariable("REDIS_KEY");
        var redis_port = Environment.GetEnvironmentVariable("REDIS_PORT");

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

    public IEnumerable<RedisRecord> GetImages()
    {
        return getImagesFromDir();
    }
}