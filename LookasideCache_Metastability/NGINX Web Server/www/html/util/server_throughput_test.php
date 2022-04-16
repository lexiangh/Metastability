<?php
srand();
$total_num_db_entries =  34511000; 
 
$mem_var = new Memcached();
$mem_var->addServer("10.158.50.15", 11211);
$servername = "10.158.61.204";
$username = "webserver";
$password = "DARK@mark37";
 
$request_type = "0"; //$_GET['request_type'] 

echo "server throughput test code\r\n";
$iter = 1;
$i = 0;
$total_completed_jobs = 0;
$experiment_minutes = 2;
$experiment_time_period = 60 * $experiment_minutes;

$total_hit_in_memcache = 0;
$total_miss = 0;

function zipf($input)
{
    $flag = 0;
    $alpha = 1.2;
  
    while ($flag < 1)
    {
        $u1 = (rand(1, 1000) / 1000);
        $u2 = (rand(1, 1000) / 1000);
        $x = floor(pow($u1, (-1 / ($alpha - 1))));
        $t = pow(1 + (1 / $x) , $alpha - 1); 
        $z = ($t / ($t - 1)) * ((pow(2, $alpha - 1) - 1) / ($u2 * pow(2, $alpha - 1)));
        if ($x <= $z && $x < $input)
        {
            $flag = 1;
        }
    }
    return $x;
}

while($i < $iter){

        $x = 0;
        $y = 0;

        $start =  microtime(true);
        while(1) {
            //$idx = rand(1, $total_num_db_entries);
            $idx = zipf($total_num_db_entries);
            switch ($request_type) {
            case "0": 
                $memcached_response =  $mem_var->get($idx); 
                //echo "idx = " . $idx . " memcache_response = " . $memcached_response. "\r\n";
                if ($memcached_response) { 
                    $x++;
                    $y++;
                }
                else {                
                    //echo "Key not found in memcached. Searching in DB\r\n";
                    $dbh =mysqli_connect($servername, $username, $password); // $backoff->run(function() {
                    //  return mysqli_connect($servername, $username, $password);
                    // });  
                    if (!$dbh)        
                        die("Unable to connect to MySQL: " . mysqli_error($dbh));

                    if (!mysqli_select_db($dbh,'metastable_test_db'))  
                        die("Unable to select database: " . mysqli_error($dbh)); 
                    
                    $sql_stmt = "SELECT * FROM large_test_table where id=" . $idx; 
                    //execute sql statement 
                    $result = mysqli_query($dbh,$sql_stmt);
                    
                    if (!$result){      
                        echo "SQL QUERY STRING: ". $sql_stmt. "\r\n";
                        die("Database access failed: " . mysqli_error($dbh)); 
                    }

                    // check if any item is present in DB 
                    $rows = mysqli_num_rows($result); 
                    if(!$rows)
                        die("No entry found for Key = " . $idx);
                    else{
                        // echo "Data found in db" . "\r\n";

                    }
                    $data_array = mysqli_fetch_array($result);
                    $stringified_data = implode("+",$data_array); 

                    //insert data to memcached
                    $mem_set_result = $mem_var->set($idx,  $stringified_data);                    
                    $result -> free_result();
                    $dbh -> close();
                    $x++;
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
            }

            $end = microtime(true);  
            $elapsed_time = ($end - $start); //1000000000; // time in seconds

            if($elapsed_time >= $experiment_time_period){
                break; 
            }         
    }
    echo "iteration ". $i . " finished.\r\n";
    $total_completed_jobs+=$x;
    $total_hit_in_memcache+= $y; 
    $i++;
}

echo "total job completed: ". $total_completed_jobs . " total hit in memcache: " . $total_hit_in_memcache . "\r\n";
echo "hit rate at memcached: " . ($total_hit_in_memcache/$total_completed_jobs) . "\r\n";
echo "throughput [server]: " . (($total_completed_jobs/$iter)/$experiment_time_period) . "\r\n";

?>