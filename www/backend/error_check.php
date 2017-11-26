<?php 
	include "Mail.php";
	$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	 
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
	$sql = "SELECT * FROM history WHERE snp_done = 3 or gns_done = 3 or gwab_done = 3 order by id desc limit 1";
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
		$boost = "../user_made_file/snp/snp_pvalue_".$u_key.".txt";#snp-pvalue file for boosting(7_FT22_pvalue_forboost_incremental)
		$p_start = $value[9];
		$p_end = $value[10];
		$step = $value[11];
		$gns_done = $value[12];
		$snp_done = $value[13];
		$boost_done = $value[14];
		$strip_pheno = stripslashes($phenotype);
		$strip_mail = stripslashes($value[3]);
		if($gns_done == 3)
		{
		$body =	"Dear GWAB user,

		Your GWAB job has occured an error when mapping SNPs to genes. 
		Disease name : $strip_pheno
		You can see the status if you click the folllowing link. http://staging.inetbio.org/gwab/status.php?u_id=$u_key

		We deeply appreciate your interest in our GWAB web-server. 

		Best wishes,
		GWAB web-server administrator";
		$sql = "UPDATE history SET gns_done='4' WHERE u_key='$u_key'";	
		}
		if($snp_done == 3)
		{
				$body =	"Dear GWAB user,

		Your GWAB job has occured an error when extracting p-value of SNPs. 
		Disease name : $strip_pheno
		You can see the status if you click the folllowing link. http://staging.inetbio.org/gwab/status.php?u_id=$u_key

		We deeply appreciate your interest in our GWAB web-server. 

		Best wishes,
		GWAB web-server administrator";
		$sql = "UPDATE history SET snp_done='4' WHERE u_key='$u_key'";	
		}
		if($boost_done == 3)
		{
				$body =	"Dear GWAB user,

		Your GWAB job has occured an error when boosting and validation stage. 
		Disease name : $strip_pheno
		You can see the status if you click the folllowing link. http://staging.inetbio.org/gwab/status.php?u_id=$u_key

		We deeply appreciate your interest in our GWAB web-server. 

		Best wishes,
		GWAB web-server administrator";
		$sql = "UPDATE history SET gwab_done='4' WHERE u_key='$u_key'";	
		}

		$mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

		$from =	"NBL support team<support@netbiolab.org>";
		$to = $strip_mail;
		$subject = "[GWAB] Your job occured an error";
		
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

 #python2.7 generate_plot_optimalP.py 10 a_disease CAD_all.txt ../files/H6Net.2014.net ../user_made_file/gns_fe74f5f1e73e831da9d6a8b82206a5c1.txt CAD ../user_made_file/snp_pvalue_fe74f5f1e73e831da9d6a8b82206a5c1.txt

		

		
		#python generate_plot_optimalP.py 10 FT_test.out floweringVern_noIEPgenes AraNet.txt FT22_chr.pos FT 7_FT22_pvalue_forboost_incremental
?>