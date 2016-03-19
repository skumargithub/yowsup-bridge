#!/bin/bash

find . -name \*.pyc -exec rm {} \;
rm -f TRIGGER_EXIT

timestamp() {
  date +"%T"
}

while :
do
	timestamp
	python run.py
	echo "Program has exited..."
        if test -f "TRIGGER_EXIT"; then
		echo "EXIT triggered, getting out!!!!!!!!!!!!!!!!!"
		exit 0
	fi
	echo "Sleeping for some time...."
	sleep $[ ( $RANDOM % 60 ) + 60]s
done
