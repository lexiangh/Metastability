<?php

$total_num_db_entries = 34511000; 
function retry_policy($policy_code){
  echo "retry policy code: " . $policy_code . "\r\n";
  switch($policy_code){
    case "0":
      Backoff::$defaultMaxAttempts = 1000;
      Backoff::$defaultStrategy = 'constant';
      Backoff::$defaultJitterEnabled = true;
      $backoff = new Backoff(10);
      $backoff->setStrategy(function($attempt) {
          echo "attempt: ". $attempt . "\r\n";
          return 10 * $attempt;
      });
      break;
    case "1":
      break;
    default: 
      break; 
  }
  return null;
}

//retry_policy(0);



$mem_var = new Memcached();
$mem_var->addServer("10.158.50.15", 11211);
$servername = "10.158.61.204";
$username = "webserver";
$password = "DARK@mark37";
 
$request_type = $_GET['request_type'];
$request_size = $_GET['request_size'];
$arrival_time = $_GET['arrival_time'];
$retry_policy = $_GET['retry_policy'];
$request_index = $_GET['request_index']; 

switch ($request_type) {
   case "0": 
     $memcached_response =  $mem_var->get($request_index); 

     if ($memcached_response) {
       //echo "Data was found in memcached\r\n";
       //echo $memcached_response;  
        echo 1; 
   } else {
       
        // echo "Key not found in memcached. Searching in DB\r\n";
         $dbh =mysqli_connect($servername, $username, $password); // $backoff->run(function() {
          //  return mysqli_connect($servername, $username, $password);
         // });  
         if (!$dbh){        
          //   die("Unable to connect to MySQL: " . mysqli_error($dbh));
           echo -1;
           exit();
        }
         if (!mysqli_select_db($dbh,'metastable_test_db'))  {
            echo -2;
            exit();
            //die("Unable to select database: " . mysqli_error($dbh));         
         }
           
         $sql_stmt = "SELECT * FROM large_test_table where id=" . $request_index; 
         //execute sql statement 
         $result = mysqli_query($dbh,$sql_stmt);
          
         if (!$result){      
               echo -3;
               exit();
              //echo "SQL QUERY STRING: ". $sql_stmt. "\r\n";
              //die("Database access failed: " . mysqli_error($dbh)); 
          }

        // check if any item is present in DB 
         $rows = mysqli_num_rows($result); 
         if(!$rows){
           echo -4;
           exit();
            //die("No entry found for Key = " . $request_index);
          }
         else{
           //echo "Data found in db" . "\r\n";
           echo 2;
         }
         $data_array = mysqli_fetch_array($result);
         $stringified_data = implode("+",$data_array); 

         //insert data to memcached
         $mem_set_result = $mem_var->set($request_index,  $stringified_data);
         if(!$mem_set_result){
           echo -5;
           exit();
           //die(" Key could not be created, key = ". $request_index. " value= ". $stringified_data.  "\r\n");
         }
         else{
           echo 3;
         }
         
         $result -> free_result();
         $dbh -> close();
   }
     break;
   case "1":
      echo "Request type 1!\r\n";
     break;
   case "2":
      echo "Request type 2!\r\n";
     break;
   default:
      echo "Unknown Request type!\r\n";
      break;
 }

?>