<?php 

$command = escapeshellcmd('./python ./googleExcelRetrieveTest.py');
$output = shell_exec($command);
echo $output;

//ob_start();
//passthru('./python ./googleExcelRetrieveTest.py');
//$output = ob_get_clean(); 

?>
