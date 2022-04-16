<?php
//fill memcached with data
ini_set('max_execution_time', '0'); // for infinite time of execution 
$servername = "DATABASE_SERVER_IP";
$username = "webserver";
$password = "DARK@mark37";
$total_num_db_entries = 34511000;
echo "throughput test code\r\n";
$iter = 10;
$i = 0;
$total_completed_jobs = 0;
$experiment_time_period = 30;


while($i < $iter){

    $x = 0;
    $start =  microtime(true);//hrtime(true);

    while(1) {
        $idx = rand(1, $total_num_db_entries);


        $dbh = mysqli_connect($servername, $username, $password); 
        //connect to MySQL server
        if (!$dbh)        
        die("Unable to connect to MySQL: " . mysqli_error());

        //if connection failed output error message 
        if (!mysqli_select_db($dbh,'metastable_test_db'))  
        die("Unable to select database: " . mysqli_error()); 
        //if selection fails output error message 

        $sql_stmt = "SELECT * FROM large_test_table where id=" . $idx; 
        //SQL select query 

        $response = mysqli_query($dbh,$sql_stmt);
        $response -> free_result();
        $dbh -> close();

        if($response){
            $x++;
        }

        $end = microtime(true);  
        $elapsed_time = ($end - $start); //1000000000; // time in seconds
        //echo $elapsed_time . "\r\n";
        if($elapsed_time >= $experiment_time_period){
            break; 
        }
     }
     $total_completed_jobs+=$x;
     echo "current iteration: " . $i . "\r\n";  
    $i++;
}


echo "throughput [database]: " . (($total_completed_jobs/$iter)/$experiment_time_period) . "\r\n";

?>


