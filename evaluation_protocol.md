# Evaluation Protocol  
Hospital Management Ontology (HMO)  
Hybrid Collaborative Ontology Design (HCOD)

## 1. Purpose of the Evaluation
This document describes the evaluation procedure used to measure the operational performance of the Hospital Management Ontology (HMO).  
The objective of the evaluation is to ensure transparency, reproducibility, and methodological rigor in the reported performance metrics.

The evaluation focuses on the following metrics:

- Data Integration Success
- Reasoning Accuracy
- Query Performance

---

## 2. Evaluation Environment

**Ontology Editor:** Protégé  
**Reasoner:** HermiT  
**Triple Store / SPARQL Engine:** Apache Jena Fuseki  
**Programming Language (Evaluation Scripts):** Python  
**Operating Environment:** [Specify OS if desired]

---

## 3. Dataset Description

The validation dataset consists of synthetic but realistic healthcare records generated to reflect real hospital workflows while preserving privacy.

**Dataset Characteristics:**
- Number of records: [e.g., 5000]
- Data type: Patient encounters and clinical data
- Format: CSV / RDF
- Source: Synthetic dataset based on real healthcare patterns

---

## 4. Evaluation Procedure

The evaluation was conducted in the following steps:

1. Loading the ontology into the reasoning environment.
2. Importing the validation dataset.
3. Mapping dataset fields to ontology classes and properties.
4. Executing reasoning and classification.
5. Running competency-question–based SPARQL queries.
6. Comparing inference results with expert-validated ground truth.
7. Calculating performance metrics.

---

## 5. Data Integration Success

### Definition
Data integration success measures the ability of the ontology to correctly map and represent incoming data.

### Formula

Data Integration Success (%) =  
(Number of successfully mapped fields / Total number of fields) × 100

### Measurement Method
- Automated mapping logs were generated.
- Mapping results were verified using schema constraints.
- Random samples were manually reviewed by domain experts.

---

## 6. Reasoning Accuracy

### Definition
Reasoning accuracy evaluates the correctness of ontology-based inference compared to expert-validated ground truth.

### Formula

Reasoning Accuracy (%) =  
(Number of correct inferences / Total number of test cases) × 100

### Measurement Method
- A set of competency-question–driven test cases was executed.
- Inferred classifications were compared with expected outcomes.
- Discrepancies were manually inspected.

---

## 7. Confusion Matrix (Optional Advanced Evaluation)

For selected classification tasks, results were also analyzed using:

- True Positives (TP)
- False Positives (FP)
- False Negatives (FN)
- True Negatives (TN)

Additional metrics:

Precision = TP / (TP + FP)  
Recall = TP / (TP + FN)  
F1-score = 2 × (Precision × Recall) / (Precision + Recall)

---

## 8. Query Performance Measurement

Query execution time was measured using SPARQL benchmarks.

Procedure:
1. Execute predefined SPARQL queries.
2. Record execution time.
3. Compute average response time.

Metric reported:
- Average query response time (seconds)

---

## 9. Validation Reliability Measures

To ensure reliability:

- Multiple test runs were performed.
- Errors were manually reviewed.
- Dataset integrity checks were applied.
- Reasoner consistency checks were executed before testing.

---

## 10. Reproducibility Instructions

To reproduce the evaluation:

1. Load the ontology from the `/ontology` folder.
2. Import the dataset from the `/dataset` folder.
3. Execute SPARQL queries from `/test-cases/sparql_queries`.
4. Run evaluation scripts in `/evaluation`.
5. Compare results with `/evaluation/results_report.csv`.

---

## 11. Versioning

Ontology Version: HMO v1.0  
Evaluation Protocol Version: 1.0  
Last Updated: 09-02-2026

---

## 12. Contact

For questions regarding evaluation methodology or reproduction steps, please contact:

Dr. Badraldeen Hassan Altahir

