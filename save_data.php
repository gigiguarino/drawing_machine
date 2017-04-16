<?php
$myfile = fopen("points.txt", "w");
$txt = $_POST['data'];
fwrite($myfile, $txt);
fclose($myfile);
?>
