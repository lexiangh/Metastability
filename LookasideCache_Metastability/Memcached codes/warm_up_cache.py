from pymemcache.client import base
import sys
 
print("Cache warmup started")
client = base.Client(('127.0.0.1', 11211))  
warm_up_size = WARM_UP_SIZE

dummy_string = "10768620+290195+5+5+203+47+515796+469964+290195+6430632+2552315418688618546+5785091512271041250+0+2.34537+4.087147+1.984295+1.49+2.20+2021-11-02+2021-11-01+2021-04-03 11:11:51+2021-08-09 17:05:21+2021-11-23 18:02:40+2021-11-23 18:02:40+13:07:07+04:58:25+2020+2020+quae possimus laboriosam similique soluta reprehenderit est.+magnam eos soluta excepturi.+Lo+Ta+excepturi quae asperiores provident at qui et ex rem omnis.+assumenda consequatur possimus sit voluptate est corporis nulla!+et unde minus distinctio!+excepturi excepturi aspernatur quisquam vitae eaque.+praesentium et quasi assumenda.+atque perferendis quasi vel assumenda!+occaecati quaerat sapiente.+eum pariatur dicta velit quia quia.+est rerum a beatae ullam numquam facere velit.+quia beatae perspiciatis id unde quasi.+et suscipit tempore nihil.+autem sunt sed voluptas qui fugit eum.+ratione placeat consequatur maiores nobis quasi.+dolorum at est et sint voluptas.+Mat+Pet+Michael+Pamela+a+a+blue+blue+0.361+0.000+0.29+0.00+290195+5+47+469964+6430632+5785091512271041250+2.34537+1.984295+2.20+2021-11-01+2021-08-09 17:05:21+2021-11-23 18:02:40+04:58:25+2020+magnam eos soluta excepturi.+Ta+assumenda consequatur possimus sit voluptate est corporis nulla!+excepturi excepturi aspernatur quisquam vitae eaque.+atque perferendis quasi vel assumenda!+eum pariatur dicta velit quia quia.+quia beatae perspiciatis id unde quasi.+autem sunt sed voluptas qui fugit eum.+dolorum at est et sint voluptas.+Pet+Pamela+a+blue+0.000+0.00"

for i in range(warm_up_size, 1, -1): 
    result = client.set(str(i), dummy_string) 

print("Cache warmup completed.")