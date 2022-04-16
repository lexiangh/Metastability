<?php
//fill memcached with data
ini_set('max_execution_time', '0'); // for infinite time of execution 
$mem_var = new Memcached();
$mem_var->addServer("10.158.50.15", 11211);
$servername = "10.158.61.204";
$username = "webserver";
$password = "DARK@mark37";
$total_num_db_entries = 34511000;

$dbh =mysqli_connect($servername, $username, $password); // $backoff->run(function() {
    //  return mysqli_connect($servername, $username, $password);
   // }); 
    //connect to MySQL server
if (!$dbh)        
    die("Unable to connect to MySQL: " . mysqli_error());


for($idx= 1653049 ; $idx< 3451100; $idx++){
    $memcached_response = $mem_var->get($idx);
    echo "KEY: " . $idx . "\r\n";

    if ($memcached_response) {
        echo "Data was found in memcached\r\n";
      //echo $memcached_response;
  } else {
    
      //echo "inside else block". "\r\n";
        //if connection failed output error message 
       if (!mysqli_select_db($dbh,'metastable_test_db'))  
           die("Unable to select database: " . mysqli_error()); 
        
        $sql_stmt = "SELECT * FROM large_test_table where id=" . $idx; 
        //echo $sql_stmt . "\r\n";
       //SQL select query              
        $result = mysqli_query($dbh,$sql_stmt);
        if (!$result)      
                die("Database access failed: " . mysqli_error()); 
       //output error message if query execution failed 
       //echo "result was fetched.". "\r\n";
       $rows = mysqli_num_rows($result); 
       //echo "rows was fetched: ". $rows. "\r\n";       
       // get number of rows returned  
       $row = mysqli_fetch_array($result);
       $stringified_data = implode("+",$row);
       //echo $stringified_data . "\r\n";  
       $mem_var->set($idx,  $stringified_data) or die(" Key could not be created \r\n");
       //echo "line after mem_set". "\r\n";
     // Free result set
       $result -> free_result();
      // echo "line before close". "\r\n";
        //echo "reached here". "\r\n";

    }   

    //echo "reached the end of inner loop". "\r\n";
}

$mysqli -> close();

?>


