<?php
    $u_id = $_GET['u_id'];
    $mysqli = new mysqli('localhost', 'gwab', 'nblrp:4p', 'gwab');
     
    if ($mysqli->connect_errno) {
        die('Connect Error: '.$mysqli->connect_error);
    }
    $sql = "SELECT * FROM history WHERE u_key = '$u_id' order by id desc limit 1";
    $result = $mysqli->query($sql) or trigger_error($mysqli->error."[$sql]");

    $arr = array();
    while($row = $result ->fetch_array(MYSQL_NUM)){
        $arr[] = $row;
    }
    $date_time = $arr[0][2];
    $gwas_file = $arr[0][4];
    $disease_file = $arr[0][5];
    $disease_name = $arr[0][6];
    if($arr[0][7] == 0)
    {
      $build = 'knownGeneHG18';
    }
    else if($arr[0][7] == 1)
    {
      $build = 'knownGeneHG19';
    }
    $residue = $arr[0][8];
    $prior_start = $arr[0][9];
    $prior_end = $arr[0][10];
    $step = $arr[0][11];
    $opt_file = "user_made_file/result/"."$u_id"."_opt";
    $opt = fopen($opt_file, "r") or die("Unable to open file!");
    $opt_line = fgets($opt);
    $regex = "/(\b|-)\d.\d+/";
    preg_match($regex, $opt_line, $matches);
    #echo $opt_line;
    #print_r($matches);
    $opt_pval = $matches[0];
    fclose($opt);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Basic Page Needs
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta charset="utf-8">
  <title>GWAB Result</title>
  <meta name="description" content="">
  <meta name="author" content="">

  <!-- Mobile Specific Metas
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- FONT
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <link href="//fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">

  <!-- CSS
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <link rel="stylesheet" href="css/normalize.css">
  <link rel="stylesheet" href="css/skeleton.css">
  <link rel="stylesheet" href="css/custom.css">
  <!-- Favicon
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <link rel="icon" type="image/png" href="images/favicon.png">
</head>
<body>
<div class="container">
  <div class="row" style="margin-top: 5%">
    <a href="index.html"><h1>GWAB</h1></a>
  </div>
</div>
  <!-- Primary Page Layout
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <div class="container">
    <div class="row">
      <div class="twelve columns" style="margin-top: 5%">
        <h3 align="center">YOUR RESULT</h3>
      </div>
    </div>
  </div>
  <div class ="container">
    <div class="row">
    <a href="user_made_file/result/genelist_<?php echo $u_id;?>.output" download>
      <p align="center">Click here to download ranked genelist of your GWAB reult</p>
    </a>
    </div>
    <div class="row">
      <div class="six columns" style="margin-top: 5%">
         <p align="center" style="text-decoration:underline; ">Validation Result</p>
        <img src="user_made_file/result/result_<?php echo $u_id; ?>.png" alt="validation result" style="width:100%">
        <p align="center">optimal p-value threshold : <?php echo $opt_pval;?></p>
      </div>
      <div class="six columns" style="margin-top: 5%">
        <table class="u-full-width">
        <caption style="text-decoration:underline; ">GWAB configuration set</caption>
          <thead>
          
          </thead>
          <tbody>
            <!--<tr>
              <th>Submit Date</th>
              <td><?php echo $date_time; ?></td>
            </tr>-->
            <tr>
              <th>Gwas Data</th>
              <td><?php echo $gwas_file; ?></td>
            </tr>
            <tr>
              <th>Disease File</th>
              <td><?php echo $disease_file ;?></td>
            </tr>
            <tr>
              <th>Disease Name</th>
              <td><?php echo $disease_name;?></td>
            </tr>
            <tr>
              <th>Build</th>
              <td><?php echo $build;?></td>
            </tr>
            <tr>
              <th>Residue</th>
              <td><?php echo $residue;?></td>
            </tr>
            <tr>
              <th>p-value Start</th>
              <td><?php echo $prior_start;?></td>
            </tr>
            <tr>
              <th>p-value End</th>
              <td><?php echo $prior_end;?></td>
            </tr>
            <tr>
              <th>p-value Step</th>
              <td><?php echo $step;?></td>
            </tr>
            <tr>
              <th>Suffles</th>
              <td>10</td>
            </tr>
            <tr>
              <th>FPR</th>
              <td>0.05</td>
            </tr>
          </tbody>
        </table>
    </div>
  </div>
  </div>

<!-- The above form looks like this -->

<!-- Always wrap checkbox and radio inputs in a label and use a <span class="label-body"> inside of it -->

<!-- Note: The class .u-full-width is just a utility class shorthand for width: 100% -->
<!-- End Document
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
<footer><p style="font-style:oblique;text-decoration:underline;">&copy;2016 NETBIO LAB @ YONSEI UNIV. All rights reserved</p></footer>
</body>
</html>
