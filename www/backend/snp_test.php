
<?php 

	$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	 
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
	$sql = "SELECT * FROM history WHERE snp_done = 0 order by id desc limit 1";
	$result = $mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

	$arr = array();
	while($row = $result ->fetch_array(MYSQL_NUM)){
   		$arr[] = $row;
	}

	foreach ($arr as &$value) {
    	$gwas_sum = "../uploads/"."gwas_".$value[1].".txt";
		$u_key = $value[1];
		$sql = "UPDATE history SET snp_done='1' WHERE u_key='$u_key'";
		echo "enter snp_send";		
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
		system("scl enable python27 'LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/opt/rh/python27/root/usr/lib64 python snp.py ".$gwas_sum." ".$u_key."'",$ret);
		echo $ret;
		if($ret == 0)
		{
			$sql = "UPDATE history SET snp_done='2' WHERE u_key='$u_key'";	
		}
		else
		{
			$sql = "UPDATE history SET snp_done='3' WHERE u_key='$u_key'";
		}
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
	}
?>