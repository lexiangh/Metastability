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
   "math"
   "math/rand"
)

 var primary *string
 var collectionName *string
 var n *int
 var requestInterval *int
 var timeOut *int
 var requestResends *int
 var timeSt time.Time // to track 1S interval
 var su int // count of successful response
 var er int // // count of failed response

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
	
	timeSt = time.Now()
	er = 0
	su = 0
	for i < *n{
		time.Sleep(time.Duration(time.Duration(*requestInterval) * time.Nanosecond) )
		go send(i,0, &waitGroup,collection)
		i++
	}

	waitGroup.Wait()
}

/*
	This function will return timeout value for certain request.
	x : choise, 0-> static timeout 3s, 1 -> exponential backoff with jitter
 */
func timeoutDetermine(x int, resends int) int { //in MilliS.
	if (x < 1) {
		return 3000; //initial
	} else {
		return int(math.Pow(2,float64(resends))) * 3000 + rand.Intn(1000);
	}
}

func send(id int, resends int, waitGroup *sync.WaitGroup, collection *mongo.Collection)   {
	defer waitGroup.Done()
	

	endT := time.Now()
	elapsedT := endT.Sub(timeSt)
	// After 1s, we will reset success and failure count.
	if (elapsedT.Milliseconds() > 1000) {
		su = 0;
		er = 0;
		timeSt = time.Now();
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutDetermine(1, resends)) * time.Millisecond ) 
   defer cancel()
	start := time.Now()
	_, err := collection.InsertOne(ctx, bson.D{{"id",id}, {"resends",resends}})
	end := time.Now()
	elapsed := end.Sub(start)
	if err != nil {
		er++
		log.Println(id, resends, "err",elapsed.Microseconds(),"")// err.Error())
      if (resends < *requestResends) {
      	// Control block. error rate is beow 40%, then we'll retry , otherwise, we wont retry.
      	if (er + su == 0 || (er * 100)/(er+su) <= 40) {
	         waitGroup.Add(1)
	         resends++
	         send(id,resends, waitGroup,collection)
	      }
         
      }

	} else {
		su++
		log.Println(id, resends, "succ", elapsed.Microseconds(),"")
	}
}
