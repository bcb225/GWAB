<?php 
	include "Mail.php";
	$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	 
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
	$sql = "SELECT * FROM history WHERE snp_done = 2 and gns_done = 2 and gwab_done = 0 order by id desc limit 1";
	$result = $mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

	$arr = array();
	while($row = $result ->fetch_array(MYSQL_NUM)){
   		$arr[] = $row;
	}

	foreach ($arr as &$value) {
    	$gwas_sum = "../uploads/"."gwas_".$value[1].".txt";
		$u_key = $value[1];
		$suffles = 10;
		#$phenotype = outputfile name
		$genelist = "../uploads/disease_".$u_key.".txt";#input genes (for validation)
		$network = "../files/H6Net.2014.net";
		$chrpos = "../user_made_file/gns/gns_".$u_key.".txt";#snp chromosome position file (FT22_chr.pos) //gns.txt
		$file_name = "../user_made_file/result/result_".$u_key;
		$phenotype = $value[6]; //input
		$phenotype = preg_replace('/\'/', "\'", $phenotype);
		$boost = "../user_made_file/snp/snp_pvalue_".$u_key.".txt";#snp-pvalue file for boosting(7_FT22_pvalue_forboost_incremental)
		$p_start = $value[9];
		$p_end = $value[10];
		$step = $value[11];
		echo $phenotype;
		$sql = "UPDATE history SET gwab_done='1' WHERE u_key='$u_key'";
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
		#sprintf("python2.7 generate_plot_optimalP.py %s %s %s %s %s %s", $suffles, $phenotype, $genelist, $network, $chrpos, $boost);
		$command = "python generate_plot_optimalP.py \"$suffles\" \"$file_name\" \"$genelist\" \"$network\" \"$chrpos\" \"$phenotype\" \"$boost\" \"$p_start\" \"$p_end\" \"$step\" \"$u_key\"";
		$command = addslashes($command);
		$redhat6_only = "scl enable python27 \"LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/opt/rh/python27/root/usr/lib64; $command\" ";
		print $command . "\n";
		print $redhat6_only . "\n";
		system($redhat6_only, $ret);
		echo $ret;
		if($ret == 0)
		{
			$sql = "UPDATE history SET gwab_done='2' WHERE u_key='$u_key'";
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

		$from =	"NBL support team<support@netbiolab.org>";
		$to = $value[3];;
		$subject = "[GWAB] Your job is finished";
		$body =	"Dear GWAB user,

		Your GWAB job has been successfully finished. 
		Disease name : $phenotype
		You can see the results if you click the folllowing link. http://staging.inetbio.org/gwab/result.php?u_id=$u_key

		We deeply appreciate your interest in our GWAB web-server. 

		Best wishes,
		GWAB web-server administrator";
		$host = "ssl://smtp.worksmobile.com";
		$port = 465;
		$username = "support@netbiolab.org";
		$password = "nblrp:5p";

		$headers = array( 'From' => $from, 'To' => $to, 'Subject' => $subject, 'Content-Type' => "text/plain; charset=utf8" );
		$params = array( 'host' => $host, 'port' => $port, 'auth' => true, 'username' => $username, 'password' => $password );

		$smtp = Mail::factory( "smtp", $params );
		$mail = $smtp->send( $to, $headers, $body );

		if (PEAR::isError($mail)) {
			echo("<p>" . $mail->getMessage() . "</p>\n" );
		}
		else
		{
			echo("<p>Message successfully sent!</p>\n");
		}
		}
		else
		{
			$sql = "UPDATE history SET gwab_done='3' WHERE u_key='$u_key'";
		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");
		}
		
	}

 #python2.7 generate_plot_optimalP.py 10 a_disease CAD_all.txt ../files/H6Net.2014.net ../user_made_file/gns_fe74f5f1e73e831da9d6a8b82206a5c1.txt CAD ../user_made_file/snp_pvalue_fe74f5f1e73e831da9d6a8b82206a5c1.txt

		

		
		#python generate_plot_optimalP.py 10 FT_test.out floweringVern_noIEPgenes AraNet.txt FT22_chr.pos FT 7_FT22_pvalue_forboost_incremental
?>
