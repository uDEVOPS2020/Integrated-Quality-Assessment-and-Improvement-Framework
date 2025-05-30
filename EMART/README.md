# EMART

This repository contains an evolution of EMART, initially presented in the paper:

Testing Microservice Architectures for Operational Reliability, by Roberto Pietrantuono, Stefano Russo, Antonio Guerriero, SOFTWARE TESTING, VERIFICATION AND RELIABILITY

All the results obtained in the experimentation of the proposed technique (called EMART) are collected. Each folder is coupled with the correspondent Research Question (RQ) as described in the original paper. In the RQ1 and RQ2 folders, results in terms of MSE and Variance are organized considering:

- the true operational profile: profile1, profile2, profile3 and variable profile
- the error attached to relative estimated profiles: 10%, 90%
In the pictures, both EMART results and Operational Testing (OT) results, used as baseline, are reported. The RQ3 contains all the results of the cost-benefit analysis considering both MSE and Variance. All considerations on the additional results with respect to those reported in the paper confirm the main conclusions described in the paper.

In the folder "code", the source code of the EMART engine is available. To run EMART, these steps need to be followed:

1. Import the source code in an IDE (e.g., Eclipse).
2. Populate the data structure Test Frame.
3. Define a Weight Matrix to build connections among Test Frames.
4. Set the values of n (number of samples to be selected), and d (a weight parameter representing the probability of adopting the weight-based sampling in the adaptive sampling algorithm, 0.5 is the default)

To repeat the experiments, it is necessary to:

1. Download and run the application defined in the paper as "experimental subjects".
2. Generate requests according to a desired profile (defined in the test frame data structure) to the interface of the components.
3. Run a monitoring infrastructure (like Metro Funnel https://github.com/dessertlab/MetroFunnel.git) to collect the methods invocation and update the information in input to the EMART engine.
