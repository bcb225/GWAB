#!/usr/bin/bash

## pre-set
allow_max_load="3.0"	#if system 1-min-avrg load is over the this value, skip running scripts
min_ram="3072"		#if available ram is under the this value, skip running scripts 

sleep_time="1"
max_sleep_time="10"


get_linux_version(){	# get RHEL/CentOS's Release Major Version
	col3=$(cat /etc/system-release | awk '{print $3}' | grep '[0-9]')
	col4=$(cat /etc/system-release | awk '{print $4}' | grep '[0-9]')

	if [ -n "$col3" ]; then
		rel=$col3
	else
		if [ -n "$col4" ]; then
			rel=$col4
		fi
	fi

	echo $rel | cut -d'.' -f1
}

gain_time(){	# add 1 sec to sleeping time
	calc=$(echo $1 + 1 | bc -s)
	if [ $calc -gt $max_sleep_time ]; then
		echo $max_sleep_time
	else
		echo $calc
	fi
}

rel_ver=$(get_linux_version)

while true; do
	sleep $sleep_time;

	## getting system stats.
	curr_date=$(date +"%Y-%m-%d %H:%M:%S")
	load_1min=$(uptime | awk -F ": " '{print $2}' | sed -e 's/ //g' | cut -d, -f1)

	if [ $rel_ver == "6" ]; then
		free_m=$(free -m | head -2 | tail -1 | awk '{freem=$4+$5+$6; print freem;}')
	elif [ $rel_ver == "7" ]; then
		free_m=$(free -m | head -2 | tail -1 | awk '{freem=$7; print freem;}')
	fi

	## print stat
	echo "[$curr_date]	load_1min, avail_ram_in_MiB = $load_1min, $free_m"

	## check load
	if [ $load_1min \> $allow_max_load ]; then
		sleep_time=$(gain_time $sleep_time)
		echo "[$curr_date]	System Load is too heavy to run. waiting $sleep_time sec."
		continue;
	fi

	## check ram
	if [ $free_m \< $min_ram ]; then
		sleep_time=$(gain_time $sleep_time)
		echo "[$curr_date]	Available ram size is too small to run. waiting $sleep_time sec."
		continue;
	fi

	sleep_time="1.0"

	## run scripts
	(echo "[$curr_date]	gns_send"; php gns_send.php) &
	(echo "[$curr_date]	snp_send"; php snp_send.php) &
	(echo "[$curr_date]	boost"; php boost.php) &
	(echo "[$curr_date]	error_check"; php error_check.php) &
done;
