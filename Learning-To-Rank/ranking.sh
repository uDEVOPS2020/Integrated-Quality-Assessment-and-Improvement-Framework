#!/bin/bash

echo "Enter the number of tests for training (type 1780 to consider the first 9 testing sessions): "  
read SZ 

#Number of samples for training
python3 csv_parsing.py $1 >> dataset.txt

head -n $SZ dataset.txt > train.txt
((SZ+=1))
tail -n $SZ dataset.txt > test.txt

python3 artifact.py
python3 score_parsing.py
