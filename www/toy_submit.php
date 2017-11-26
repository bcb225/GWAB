<?php
header('Content-type: text/html; charset=utf-8'); 
     include "Mail.php";
$mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
	if ($mysqli->connect_errno) {
	    die('Connect Error: '.$mysqli->connect_error);
	}
#print_r($_POST);
#print_r($_FILES);


if (isset($_POST)){ 
	$key = md5(microtime().rand());
     $save_dir = "uploads/";

     $gwas_dest = $save_dir ."gwas_".$key.".txt";
     $gwas_source = "files/CAD_lt0.01_input.txt";
     copy ( $gwas_source , $gwas_dest );

     $disease_dest = $save_dir ."disease_".$key.".txt";
	$disease_source = "files/CAD.txt";
     copy ( $disease_source , $disease_dest );
	$subject = $_POST['prior_input'];
	$pattern = '/[\S|-]([0-9]*[.])?[0-9]+/';
	preg_match_all($pattern,$subject, $matches,PREG_PATTERN_ORDER);
	date_default_timezone_set('Asia/Seoul');
	$date_time = date("Y-m-d H:i:s",time());
	$email=addslashes($_POST['email_input']);
	$build=$_POST['build_input'];
	$residue=$_POST['residue_input'];
	$prior_start=$matches[0][0];
	$prior_end=$matches[0][1];
	$interval=$_POST['range_input'];
	$gwas=addslashes($_POST['ex_gwas_input']);
	$disease_file = addslashes($_POST['ex_disease_set']);
	$disease_name = addslashes($_POST['ex_disease_input']);
	#echo $build;

	$sql = "INSERT INTO history (u_key,date_time,email, gwas,disease_file ,disease_name,build,residue,prior_start,prior_end,step,gns_done,snp_done,gwab_done)
	VALUES ('".$key."','".$date_time."','".$email."','".$gwas."','".$disease_file."','".$disease_name."','".$build."','".$residue."','".$prior_start."','".$prior_end."','".$interval."','0','0','0')";
     $strip_disease = stripslashes($disease_name);
	if ($mysqli->query($sql) === TRUE) {
	#echo "New record created successfully";
          $from =   "NBL support team<support@netbiolab.org>";
          $to = $email;
          $subject = "[GWAB] Your job is submitted";
          $body =   "Dear GWAB user,

          Your GWAB job has been successfully submitted. 
          Disease name : $strip_disease
          You can see the status of your GWAB job if you click the folllowing link. http://staging.inetbio.org/gwab/status.php?u_id=$key

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
               #echo("<p>" . $mail->getMessage() . "</p>\n" );
          }
          else
          {
               #echo("<p>Message successfully sent!</p>\n");
          }
          $status_page = "http://staging.inetbio.org/gwab/status.php?u_id=".$key;
	header("Refresh:0; url=$status_page");
          
	} else {
	#echo "Error: " . $sql . "<br>" . $mysqli->error;
	header("Refresh:0; url=error.html");
	}
	$mysqli->close();
}
?>
