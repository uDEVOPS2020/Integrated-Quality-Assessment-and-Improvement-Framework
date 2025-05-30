## Use case 4 

This folder contains the code and data to run the feature stability analysis in  Just-In-Time Defect Prediction (JIT-DP) example.

**Dataset**. This folder contains the dataset used as illustrative example for this use case. The dataset consists of commit data for 6 open source applications. It is cloned from a JIT-DP research work repository (https://github.com/ZZR0/ISSTA21-JIT-DP). As in [1], the generation procedure cosists of data extraction through python scripts, and labelling by the SZZ algorithm.

Each subject dataset has the following columns: 
_id | date | ns | nd | nf | entropy | la | ld | lt | fix | ndev | age | nuc | exp | rexp | sexp

Each row refers to a commit.   
 
**Code**. Python code files/scripts to: i) perform defect prediction on a dataset in the same format as the Dataset's folder files; this includes code for training the Random Forest and Logistic Regression models. Feature stability is computed according to the algorithm described in [2]. ii) Random Forest algorithm represent the worst case, in which each tree considers different features at each execution; Logistic Regression represents the best case since the selected features (the ones with a positive coefficient) are very often the same.  

To reproduce:  run the artifact_RF.py and artifact_LR.py scripts. 

*Prerequisites*: 
Python (version >3)

*Commands*: 
>  Run the "python artifact_RF.py" script to run the feature stability on the Random Forest model.
>  Run the "python artifact_LR.py" script to run the feature stability on the Logistic Regression model.

**Results**. The output reports the feature importance of each feature for the considered model (RF: Random Forest, LR: Logistic Regression), and the feature stability value computed as in [2]. This can be useful to assess which metrics are the best predictors not only from the accuracy point of view, but from the stability perspective. 


[1] Zhengran Zeng, Yuqun Zhang, Haotian Zhang, and Lingming Zhang. 2021. Deep just-in-time defect prediction: how far are we? In Proceedings of the 30th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2021). Association for Computing Machinery, New York, NY, USA, 427–438. https://doi.org/10.1145/3460319.3464819

[2] Sarah Nogueira, Konstantinos Sechidis, and Gavin Brown. 2017. On the stability of feature selection algorithms. <i>J. Mach. Learn. Res.</i> 18, 1 (January 2017), 6345–6398.
