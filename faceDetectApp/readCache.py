from os import access
import redis

r = redis.StrictRedis(host='facesink002.redis.cache.windows.net', 
                        port=6380,
                        db=0,
                        password='5Y79PwhUuJiNaasMX0sRSdbpIMC3LJjF6AzCaJtpPhw=',
                        ssl=True)

#for key in r.scan_iter("*"):
#    print(key)
#    # delete the key
#    r.delete(key)
if True:
    with r.monitor() as m:
        for command in m.listen():
            print(command["command"])