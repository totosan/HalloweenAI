var redis = new RedisAccess();
redis.GetImages().ToList().ForEach(x => Console.WriteLine(x));