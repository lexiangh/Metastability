<?php

//$total_num_db_entries = 34511000; 
$total_num_db_entries = 140000;
$database_query_weight = DATABASE_QUERY_WEIGHT;
$servername = "DATABASE_SERVER_IP";
$username = "metastable";
$password = "hello@123";
$memcached_server = "MEMCACHED_SERVER_IP";
//$request_type = $_GET['request_type'];
//$request_size = $_GET['request_size'];
//$arrival_time = $_GET['arrival_time'];
//$retry_policy = $_GET['retry_policy']; 
$request_index = $_GET['request_index'];     
$mem_var = new Memcache();
$mem_var->pconnect($memcached_server,11211); 

$memcached_response =  $mem_var->get($request_index) ;   
if ($memcached_response) {
    #echo "Data was found in memcached\r\n";
    //echo $memcached_response;  
   echo 1; 
  
} else 
{  

      $current_index = $request_index;
      $dbh =mysqli_connect($servername, $username, $password);

      if (!$dbh){        
        //   die("Unable to connect to MySQL: " . mysqli_error($dbh));
        echo -94;
        exit();
      }
      if (!mysqli_select_db($dbh,'metastable_test_db'))  {
          echo -94;
          exit();
          //die("Unable to select database: " . mysqli_error($dbh));         
      }

        for ($y = 0; $y < 100  ; $y++){

              $sql_stmt2 = "SELECT L2.id  from large_test_table L1 join large_test_table L2 on L1.tcol04 = L2.id where  L1.id = " . $current_index;          
              $result = mysqli_query($dbh,$sql_stmt2);

              if (!$result){      
                  echo -95 ;
                  exit();
              }

              $rows = mysqli_num_rows($result); 
            
              if(!$rows){
                  echo -96;
                  exit();
                  }          

              $data_array = mysqli_fetch_array($result);  
              $current_index = $data_array[0];
      }


      $sql_stmt3 = "SELECT *  from large_test_table L1 join large_test_table L2 on L1.tcol04 = L2.id where  L1.id = " . $current_index;
      $result = mysqli_query($dbh,$sql_stmt3);
      $data_array = mysqli_fetch_array($result);
      $result -> free_result();
      $dbh -> close();
      
      
      $stringified_data = implode("+",$data_array);  
      #echo $stringified_data . "\n";
      $mem_set_result = $mem_var->set($request_index,  $stringified_data);
      if(!$mem_set_result){
          echo -97;
          exit();
          }

      echo 2;   

  }
          
 $mem_var->close();
 

 ?>
