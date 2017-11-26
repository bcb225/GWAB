
<?php 

	$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	 
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
	$sql = "SELECT * FROM history WHERE gns_done = 0 order by id desc limit 1";
	$result = $mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

	$arr = array();
	while($row = $result ->fetch_array(MYSQL_NUM)){
   		$arr[] = $row;
	}

	foreach ($arr as &$value) {
    	$gwas_sum = "../uploads/"."gwas_".$value[1].".txt";

    	switch ($value[7]) {
		case 0:
		    #$gene_file = "../files/".'knownGeneHG18.csv';
			$gene_file = "../files/".'grpKnownGeneHG18.csv';
		
		    break;
		case 1:
		    $gene_file = "../files/".'grpKnownGeneHG19.csv';
		    break;
		case 2:
		    echo "no such file";
		    break;
		default:
			break;
		}

		$u_key = $value[1];
		$range = $value[8];
		$sql = "UPDATE history SET gns_done='1' WHERE u_key='$u_key'";
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
		echo "enter gns_send";
		echo $range;
		system("scl enable python27 'LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/opt/rh/python27/root/usr/lib64 python gns.py ".$gwas_sum." ".$gene_file." ".$u_key." ".$range."'",$ret);
		if($ret == 0)
		{
			$sql = "UPDATE history SET gns_done='2' WHERE u_key='$u_key'";	
		}
		else
		{
			$sql = "UPDATE history SET gns_done='3' WHERE u_key='$u_key'";
		}
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
	}
?>