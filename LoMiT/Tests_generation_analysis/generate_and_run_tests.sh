#!/bin/sh

CAMPAIGN_FOLDER=./campaign_ss

NEW_SWAGGER_FOLDER=/home/train/uTest/clientCommands/initFiles/JSONFiles_ss_burp

NEW_SH_FOLDER=/home/train/uTest/clientCommands

NEW_TXT_FOLDER=/home/train/uTest/clientCommands/initFiles

UTEST_FOLDER=/home/train/uTest/clientCommands/output

rm jumped.txt

RUNS=`ls $CAMPAIGN_FOLDER`

for RUN in $RUNS
do

    echo $RUN

    # PREPARE ENV
    rm -rf $NEW_SWAGGER_FOLDER/*
    JSON_FILES=`ls $CAMPAIGN_FOLDER/$RUN/*.json | wc -l`
    if [ "$JSON_FILES" -eq "0" ]; then
	    echo "$RUN" >> jumped.txt
	    echo "Jumped $RUN"
	    continue;
    fi
    cp $CAMPAIGN_FOLDER/$RUN/*.json $NEW_SWAGGER_FOLDER
    
    cp $CAMPAIGN_FOLDER/$RUN/JSONFiles_ss.txt $NEW_TXT_FOLDER
    
    cp $CAMPAIGN_FOLDER/$RUN/init-execute-clear_ss.sh $NEW_SH_FOLDER
    rm -rf $CAMPAIGN_FOLDER/$RUN/uTestOutput
    rm -rf $CAMPAIGN_FOLDER/$RUN/trainTicket_logs_during_test
    rm -rf $UTEST_FOLDER/*

    # CLEAN SS
    PATHS=`sudo ls /var/lib/docker/containers`
    NUM_CONTAINERS=`echo "${PATHS}" | wc -l`

    echo $NUM_CONTAINERS

    echo "Cleaning log files..."
    for CONTAINER in $PATHS
    do
        sudo truncate -s 0 /var/lib/docker/containers/$CONTAINER/$CONTAINER-json.log
    done

    echo "...Done"


    # GENERATE AND RUN TESTS
    HOME=`pwd`

    cd $NEW_SH_FOLDER
    sh init-execute-clear_ss.sh

    cd $HOME

    # GET uTEST outuput
    mkdir $CAMPAIGN_FOLDER/$RUN/uTestOutput
    cp $UTEST_FOLDER/* $CAMPAIGN_FOLDER/$RUN/uTestOutput

    # GET trainTicket logs
    
    mkdir $CAMPAIGN_FOLDER/$RUN/ss_logs_during_test/
    mkdir $CAMPAIGN_FOLDER/$RUN/ss_logs_during_test/logs
    

    echo "Retreiving log files..."

    for CONTAINER in $PATHS
    do
        CONTAINER_ID=`sudo cat /var/lib/docker/containers/$CONTAINER/hostname`
        echo $CONTAINER_ID
        CONTAINER_NAME=`sudo docker ps --format "{{.ID}} {{.Names}}" | grep ${CONTAINER_ID} | awk '{print $2}'`
        sudo docker ps --format "{{.ID}} {{.Names}}" | grep $CONTAINER_ID | awk '{print $2}'
        echo $CONTAINER_NAME
       
        sudo cp /var/lib/docker/containers/$CONTAINER/$CONTAINER-json.log $CAMPAIGN_FOLDER/$RUN/ss_logs_during_test/logs/$CONTAINER_NAME.log
        
        sudo chmod 666 $CAMPAIGN_FOLDER/$RUN/ss_logs_during_test/logs/$CONTAINER_NAME.log
    done

    echo "...Done"

    

    # CLEAN ENV
    
    rm $NEW_TXT_FOLDER/JSONFiles_ss.txt
    
    rm $NEW_SH_FOLDER/init-execute-clear_ss.sh
    rm $NEW_SWAGGER_FOLDER/*.json


done


cp -r $NEW_TXT_FOLDER/BCK-JSONFiles_ss_burp/* $NEW_SWAGGER_FOLDER

cp -r $NEW_TXT_FOLDER/BCK-JSONFiles_ss.txt $NEW_TXT_FOLDER/JSONFiles_ss.txt

cp -r $NEW_SH_FOLDER/BCK-init-execute-clear_ss.sh $NEW_SH_FOLDER/init-execute-clear_ss.sh
