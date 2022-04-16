<?php
$servername = "DATABASE_SERVER_IP";
$username = "metastable";
$password = "hello@123";
 
   $dbh = mysqli_connect($servername, $username, $password); 
        //connect to MySQL server
   if (!$dbh)        
        die("Unable to connect to MySQL: " . mysqli_error());
    
        //if connection failed output error message 
    if (!mysqli_select_db($dbh,'metastable_test_db'))  
        die("Unable to select database: " . mysqli_error()); 
    //if selection fails output error message 
    
        $sql_stmt = "SELECT * FROM large_test_table where id=5"; 
    //SQL select query 
    
     $result = mysqli_query($dbh,$sql_stmt);
     //execute SQL statement 

        if (!$result)     
                die("Database access failed: " . mysqli_error()); 
        //output error message if query execution failed 

                $rows = mysqli_num_rows($result); 
                // get number of rows returned 
    
        if ($rows) {     
    
        while ($row = mysqli_fetch_array($result)) {         
           echo 'ID: ' . $row['id'] . "\r\n";
           echo 'tcol01: ' . $row['tcol01'] . "\r\n";
           echo 'tcol02: ' . $row['tcol02'] . "\r\n";
           echo 'tcol03: ' . $row['tcol03'] . "\r\n";
           echo 'tcol04: ' . $row['tcol04'] . "\r\n";
           echo 'tcol05: ' . $row['tcol05'] . "\r\n";
           echo 'tcol06: ' . $row['tcol06'] . "\r\n";
      
        } 
} 

?>



