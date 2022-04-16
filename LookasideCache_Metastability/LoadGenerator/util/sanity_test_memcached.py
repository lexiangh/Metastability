from pymemcache.client import base
import sys
  
client = base.Client(('10.158.61.218', 11211))  
 
for i in range(1, 11):
    result = client.get(str(i))
    print(result)
 