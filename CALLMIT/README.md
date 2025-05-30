
# Replication Package for *Microservices Performance Testing with Causality-enhanced Large Language Models*

This repository contains the replication package for the study titled **"Microservices Performance Testing with Causality-enhanced Large Language Models"**.The package includes all the necessary resources to reproduce the results presented in the study.

---

## Repository Structure

```
├── statistical_analysis/                 # Scripts for data analysis
│   ├── script.r                          # Dunn Test
│   ├── datasets_generation.py            # Script for preparing data
│   ├── datasets                          # Prepared Datasets  
│   ├── results                           # Statistical Tests Results  
├── data/                                 # Historical datasets
├── results/                              # Output results
│   ├── {LLM}/                            # Results organized by LLM
│        ├── {subject}/                   # Results organized by subject
│             ├── {strategy}/             # Results organized by strategies
├── generation_script_gemini.py           # Main script to run all experiments with Gemini
├── generation_script_phi3_5.py           # Main script to run all experiments with Phi3.5
├── requirements.txt                      # Python dependencies
├── utility.py                            # causal graph construction, causal path selection strategies, prompt generation
└── README.md                             # Documentation file (this file)
```

---

## Requirements

The following tools and dependencies are required to replicate the study:

- **Python**: Version 3.10
- **Dependencies**: Listed in `requirements.txt`

---

## Setup Instructions

1. **Clone the repository**:
   - Clone the repository
   - Navigate to the root directory of the repository

2. **Set up the environment**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Replication Steps

1. **Generate Workload Configurations**:
   Run the script to execute all the experiments
   ```bash
   python generation_script_gemini.py
   python generation_script_phi3_5.py
   ```

2. **Reproduce Results**:
   All outputs will be stored in the `results/` directory.

3. **Perform Analysis**:
   - Prepare results:
     ```bash
     python datasets_generation.py
     ```
   - Run statistical tests:
     ```bash
     Rscript statistical_analysis/script.r
     ```

---

Refer to the manuscript for a detailed explanation of the results.
