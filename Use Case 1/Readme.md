
## Use case 1. Test case prioritization via Learning to rank techniques. 

This folder contains the dataset and code to reproduce the test prioritization example we have used to test the feasibility of the strategy: 

**Dataset**. *testFeatures.csv*. This is the dataset used as illustrative example for this use case. It is derived by running a load on a well-known open-source benchmark for microservice  architecture (MSA), named Train Ticket [1].  The application simulates a train ticket booking system, composed of 41 microservices communicating to each other via REST over HTTP. Train ticket is  polyglot (e.g., Java, golang, Node.js, etc). 

**Workload generation**: 

The dataset is automatically generated with a teseting tool we are developing in the context of the project's WP2, called [uTest](https://github.com/uDEVOPS2020/Integrated-Quality-Assessment-and-Improvement-Framework/tree/main/MacroHive/uTest). The tool generates tests starting from microservices' OpenAPI specifications. Configured in *pairwise mode*, the tool generated 4690 test cases by a combinatorial testing strategy. 

The so-obtained dataset has the following columns: 

testID | HTTP status code | Response Time | URL | HTTP method | Input Class 1 | ... | Input Class N |

Each row represents an executed test. 

**Training and test sets generator**. The training and test sets are generated through the csv_parsing.py script. The datasets are encoded in the format required by RankLib to perform the training and the prioritization.

**Prioritization**. *Response Time* and *status code* are both considered to perform the prioritization. The ranking score is computed as follows: ranking_score = response_code+1/(response_time) * 100. The response codes higher than or equal to 400 correspond to failed tests; at the same time, a lower  response time implies a higher  priority of the test. As result, the higher the value of the ranking score, the higher the priority of the considered test.

**Results**. The output of the Learning-to-Rank algorithms are ordered lists of test IDs (column "1"). Testers should run the tests according to this list in order to expose failures (both as failing statuts code and as high response time) earlier. 

**Code**. Python code files/scripts to: i) generate training and test sets, ii) train and execute the Lerning to Rank techniques, iii) build the ordered list of testIDs. 

*Prerequisites*: 

Python (version >3), JVM/JRE (version > 1.8). 

Libraries: 

RankLib library (Dang, V. “The Lemur Project-Wiki-RankLib.” Lemur Project,[Online]. Available at http://sourceforge.net/p/lemur/wiki/RankLib)


*Commands*: 

>  Run the "sh ranking.sh" script to perform the ranking of the selected test dataset.




[1]. [TrainTicket](https://github.com/FudanSELab/train-ticket)
