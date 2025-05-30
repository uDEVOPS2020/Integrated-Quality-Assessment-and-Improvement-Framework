# README

This folder contains the scripts for perform both the fine-tuning of the transformer and the inference:

+ `dependencies.py`: installs all the dependecies needed to run both the fine-tuning and inference of the transformer
+ `fine-tuning.py`: performs the fine-tuning of the transformer in order to let it generate services sequence starting from logs:

   - Input: 
   
     - path to the training dataset
     - mapping of the services

   - Output:

     - Pre-trained model

+ `inference.py`: use the fine-tuned model to perform inference:

   - Input:

     - path to the fine-tuned model
     - testing and validation datasets
     - mapping of the services

   - Output:

     - output dataset, with the list of services inferred by the trasfomer starting from logs
     - cosine similarity evaluation of logs using validation set
     - cosine similarity evaluation of service sequences
     - levenshtein_distance evaluation of service sequences