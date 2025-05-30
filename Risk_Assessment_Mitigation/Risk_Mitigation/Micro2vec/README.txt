
This repository accompanies the submission of the manuscript:
Micro2vec: Anomaly Detection in Microservices Systems by Mining Numeric Representations of Computer Logs

co-authored by

Marcello Cinque*, Raffaele Della Corte*, and Antonio Pecchia**
*Università degli Studi di Napoli Federico II
**Università degli Studi del Sannio

to JOURNAL OF NETWORK AND COMPUTER APPLICATIONS.


CONTENT:

This repo contains the following folders/sub-folders:

+ Training
+ Test
	+ AUTH	
	+ DEL
	+ DOS
	+ KILL
	+ NORMATIVE	
	+ REG
		
Each folder/sub-folder contains the following set of 13 logs (*):	

astaire.txt
bono.txt
cassandra.txt
chronos.txt
ellis.txt
homer.txt
homestead.txt
homesteadaccess.txt
homesteadprov.txt
ralf.txt
ralfaccess.txt
sprout.txt
sproutaccess.txt


NOTE:

1) 'Training' logs are used to tune the detection approach presented in the paper. 

2) 'Test' logs are collected within normative/anomalous events. They are used to 
test the proposed approach, and they are collected by means of controlled experiments.

3) Training-Test logs are collected with independent runs of the system in hand.

REGULAR EXPRESSIONS
This repository also provides the regex.txt file, which contains regular expressions used in our study as well as for replication purposes. 


(*) Some files are missing due to GitHub space limitations. Contact us in case.
CONTACT:

For any further information please contact the Authors:

macinque@unina.it
raffaele.dellacorte2@unina.it
antonio.pecchia@unisannio.it
