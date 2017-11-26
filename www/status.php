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
    if($arr[0][12] == 0)
    {
      $gns_status = '<th style="color : orange">Not Yet</th>';
    }
    else if($arr[0][12] == 1)
    {
      $gns_status = '<th style="color : blue">Running</th>';
    }
    else if($arr[0][12] == 2)
    {
      $gns_status = '<th style="color : green;">Done</th>';
    }
    else if($arr[0][12] == 3 || $arr[0][12] == 4)
    {
      $gns_status = '<th style="color : red;">Error</th>';
    }

    if($arr[0][13] == 0)
    {
      $snp_status = '<th style="color : orange">Not Yet</th>';
    }
    else if($arr[0][13] == 1)
    {
      $snp_status = '<th style="color : blue">Running</th>';
    }
    else if($arr[0][13] == 2)
    {
      $snp_status = '<th style="color : green;">Done</th>';
    }
    else if($arr[0][13] == 3 || $arr[0][13] == 4)
    {
      $snp_status = '<th style="color : red;">Error</th>';
    }

    if($arr[0][14] == 0)
    {
      $boost_status = '<th style="color : orange">Not Yet</th>';
    }
    else if($arr[0][14] == 1)
    {
      $boost_status = '<th style="color : blue">Running</th>';
    }
    else if($arr[0][14] == 2)
    {
      $boost_status = '<th style="color : green;">Done</th>';
    }
    else if($arr[0][14] == 3 || $arr[0][14] == 4)
    {
      $boost_status =  '<th style="color : red;">Error</th>';
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Basic Page Needs
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta charset="utf-8">
  <title>GWAB Status</title>
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
        <h3 align="center">YOUR STATUS</h3>
        <p align="center">Link of this page is sent to your email.<br>You can close this page while GWAB job is still running.</p>
      </div>
    </div>
  </div>
  <div class ="container">
    <div class="row">
      <div class="six columns" style="margin-top: 5%">
        <table class="u-full-width">
        <caption style="text-decoration:underline; ">GWAB job running status</caption>
          <thead>
            <tr>
            <th>
              SNP Mapping
            </th>
            <th>
              P-value Extracting
            </th>
            <th>
              Boosting &#38; Validation
            </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <?php echo $gns_status; ?>
              <?php echo $snp_status; ?>
              <?php echo $boost_status; ?>
            </tr>
          </tbody>
          </table>
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
