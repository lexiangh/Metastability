package main

import (
	"context"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"log"
	"sync"
	"time"
   "flag"

)

 var primary *string
 var collectionName *string
 var n *int
 var requestInterval *int
 var timeOut *int
 var requestResends *int



func main() {

   primary = flag.String("primary","127.0.0.1","Primary DB Url")
   collectionName = flag.String("collection","default","Collection name")
   n = flag.Int("n",100000,"Total requests")
   requestInterval = flag.Int("interval",120000,"Pause between requests in nanoseconds")   //nano seconds to microseconds divide by 1,000
   timeOut = flag.Int("timeout",3,"Timeout for requests in seconds")
   requestResends = flag.Int("resends",100000,"Number of resend attempts") //default essentially unlimited resends

   flag.Parse()

   
	log.SetFlags(log.Lmicroseconds)


	uri := "mongodb://" + *primary

	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(uri))

	if err != nil {
		log.Println(err)
	}


	dbName := "examples"


	collection := client.Database(dbName).Collection(*collectionName)
   
	i:=0
	var waitGroup sync.WaitGroup
	waitGroup.Add(*n)
	for i < *n{
		time.Sleep(time.Duration(time.Duration(*requestInterval) * time.Nanosecond) )
		go send(i,0, &waitGroup,collection)
		i++
	}
	waitGroup.Wait()




}


func send(id int, resends int, waitGroup *sync.WaitGroup, collection *mongo.Collection)   {
	defer waitGroup.Done()

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(*timeOut) * time.Second  ) 
   defer cancel()
	start := time.Now()
	_, err := collection.InsertOne(ctx, bson.D{{"id",id}, {"resends",resends}})
	end := time.Now()
	elapsed := end.Sub(start)
	if err != nil {
		log.Println(id, resends, "err",elapsed.Microseconds(),"")// err.Error())
      if (resends < *requestResends) {
         waitGroup.Add(1)
         resends++
         send(id,resends, waitGroup,collection)
      }

	} else {
		log.Println(id, resends, "succ", elapsed.Microseconds(),"")
	}



}
