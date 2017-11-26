<?php 
	$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	 
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
	$sql = "UPDATE history SET done='2' WHERE id='$argv[1]'";
	$result = $mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
?>