<?php
//fill memcached with data
$memcached_server = "MEMCACHED_SERVER_IP"
ini_set('max_execution_time', '0'); // for infinite time of execution 
$mem_var = new Memcached();
$mem_var->addServer($memcached_server , 11211); 
echo "throughput test code\r\n";
$iter = 10;
$i = 0;
$total_completed_jobs = 0;
$experiment_time_period = 30;
$total_num_db_entries = 34511000;

while($i < $iter){

    $x = 0;
    $start =  microtime(true);//hrtime(true);

    while(1) {
        $idx = rand(1, $total_num_db_entries);
        $response = $mem_var->get($idx);
        #echo $response;
        if($response){
            $x++;
         //   echo "key found!! \r\n";
        }
        else{
            //echo "key= " . $idx . " not found\r\n";
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


echo "throughput[memcached]: " . (($total_completed_jobs/$iter)/$experiment_time_period) . "\r\n";


?>


