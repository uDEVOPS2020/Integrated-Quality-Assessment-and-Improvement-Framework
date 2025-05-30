# README

This repo contains two zip archives, accompanying the submission of the manuscript:

_Micro2vec: Anomaly Detection in Microservices Systems by Mining Numeric Representations of Computer Logs_

co-authored by

_Marcello Cinque*, Raffaele Della Corte*, and Antonio Pecchia**_

_*Università degli Studi di Napoli Federico II_
_**Università degli Studi del Sannio_

and submitted for evaluation to _JOURNAL OF NETWORK AND COMPUTER APPLICATIONS_.


## JNCA2022ATCLogs-Regex.zip 


This archive is provided to researchers, who wish to have a deep look into the regular expressions used in our study as well as for replication purposes. 

The archive contains the `Regex.txt` file, which provides the list of regular expressions used in our Air Traffic Control case study.



## JNCA2022EventLogs.zip 

This archive contains the following folders/sub-folders:

+ `Training`
+ `Test`
	+ `AUTH`
	+ `DEL`
	+ `DOS`
	+ `KILL`
	+ `NORMATIVE`
	+ `REG`
		
Each folder/sub-folder contains the following set of 13 logs:	

+ `astaire.txt`
+ `bono.txt`
+ `cassandra.txt`
+ `chronos.txt`
+ `ellis.txt`
+ `homer.txt`
+ `homestead.txt`
+ `homesteadaccess.txt`
+ `homesteadprov.txt`
+ `ralf.txt`
+ `ralfaccess.txt`
+ `sprout.txt`
+ `sproutaccess.txt`


NOTE:

1) `Training` logs are used to tune the detection approach presented in the paper. 

2) `Test` logs are collected within normative/anomalous events. They are used to 
test the proposed approach, and they are collected by means of controlled experiments.

3) `Training-Test` logs are collected with independent runs of the system in hand.


