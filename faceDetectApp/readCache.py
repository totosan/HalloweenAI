import itertools
from os import access
import redis
from itertools import zip_longest

r = redis.StrictRedis(host='facesink002.redis.cache.windows.net', 
                        port=6380,
                        db=0,
                        password='5Y79PwhUuJiNaasMX0sRSdbpIMC3LJjF6AzCaJtpPhw=',
                        ssl=True)

#for key in r.scan_iter("*"):
#    print(key)
#    # delete the key
#    r.delete(key)

# iterate a list in batches of size n
def batcher(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args)

def iterateInBatches():
    # in batches of 500 delete keys matching user:*
    for keybatch in batcher(r.scan_iter('*'),500):
        #r.delete(*keybatch)
        print(keybatch)

iterateInBatches()

if False:
    with r.monitor() as m:
        for command in m.listen():
            print(command["command"])