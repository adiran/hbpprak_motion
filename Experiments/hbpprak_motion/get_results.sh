#!/bin/bash

if [ -n "$1" ]
then
    if [ -n "$2" ]
    then
        filename=$2
    else
        filename=result.csv
    fi
    path=$(rosservice call /ros_cle_simulation/${1}/get_CSV_recorders_files)
    path=${path%\"*}
    path=${path#*\"}
    path=${path#*\"}
    path=${path#*\"}
    if [[ $path == /tmp* ]]
    then
        cp $path ./$filename
        # ros gives a file with unnecessary newlines so we delete them
        sed -i ':a;N;$!ba;s/\n / /g' ./$filename
        echo "copied file"
        rm $path
        echo "deleted tmp file"
    else
        echo "something went wrong, maybe the experiment stopped or you get the wrong id"
    fi
    echo $path
else
    echo "wrong usage: you need to give the experiment id as the first parameter"
    echo "you get the id if you call rosservice list while your experiment is running and"
    echo "look for a bunch of lines that start with /ros_cle_simulation/."
    echo "The number after the / is the current experiment id."
    echo "second parameter can be a filename. if no filename is provided the content is"
    echo "saved to result.csv"
fi