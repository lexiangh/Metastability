from pymemcache.client import base
import sys

args_len = len(sys.argv[1:])

memcached_host = '172.31.1.84'

if(args_len != 1):        
        print("enter valid parameter, 1 param for size")
        exit()

print("Trigger started, size = " + str(sys.argv[1:][0])) 

trigger_size = int(sys.argv[1:][0])  
client = base.Client(( memcached_host, 11211))  
 
if(trigger_size > 0):
        for i in range(1, trigger_size +1): 
                client.delete(str(i))
elif(trigger_size == -1):
        client.flush_all()
        print("flushed memcached") 
 

"""
for i in range(1, trigger_size +1): 
        result = client.get(str(i))
        print(str(result))

test_key = "test_key"
test_value = "test value"
client.set(test_key, test_value)
get_result = client.get(test_key)
print("get: " + str(get_result))
client.delete(test_key)
get_result_after_delete = client.get(test_key)
print(str(get_result_after_delete))
"""

