#!/usr/bin/env python3
"""
Hospital Management Ontology - SPARQL Query Validation
Author: Dr. Badraldeen Hassan
Date: 2025
Description: Comprehensive SPARQL queries for validating the Hospital Management Ontology
Repository: https://github.com/BadrHsnAltahir/Hospital-Management-Ontology-Design-Pattern
"""

from rdflib import Graph, Namespace, RDF, RDFS, XSD, OWL
from rdflib.plugins.sparql import prepareQuery
import datetime

# Initialize the ontology graph
g = Graph()

# Load the ontology
print("Loading Hospital Management Ontology...")
g.parse("Ontology/HospitalManagementOntologyDesignPattern.xml", format="xml")
print(f"Ontology loaded successfully. Total triples: {len(g)}")

# Define namespaces
HMO = Namespace("http://www.semanticweb.org/healthcare-ontology#")
FHIR = Namespace("http://hl7.org/fhir/")
SCHEMA = Namespace("http://schema.org/")

# Bind namespaces for cleaner query results
g.bind("hmo", HMO)
g.bind("fhir", FHIR)
g.bind("schema", SCHEMA)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

def execute_query(query, description, limit=10):
    """
    Execute SPARQL query and print results with proper formatting
    """
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")
    
    try:
        results = g.query(query)
        count = 0
        
        for row in results:
            print(" | ".join([f"{str(value):30}" for value in row]))
            count += 1
            if count >= limit:
                print("... (results limited)")
                break
        
        if count == 0:
            print("No results found")
            
        print(f"Total results: {count}")
        
    except Exception as e:
        print(f"ERROR executing query: {str(e)}")

def run_clinical_queries():
    """Clinical Domain Queries - Patient Care & Treatment"""
    print("\n" + "="*100)
    print("CLINICAL DOMAIN QUERIES - PATIENT CARE & TREATMENT")
    print("="*100)
    
    # Query 1: Elderly patients with appointments this week
    q1 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?patient ?firstName ?lastName ?age ?appointmentDate ?doctorName ?reason
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:dateOfBirth ?dob .
      ?patient hmo:hasAppointment ?appt .
      ?appt hmo:appointmentDate ?appointmentDate .
      ?appt hmo:supervisedBy ?doctor .
      ?appt hmo:reasonForVisit ?reason .
      ?doctor hmo:firstName ?docFirstName .
      ?doctor hmo:lastName ?docLastName .
      BIND (CONCAT(?docFirstName, " ", ?docLastName) AS ?doctorName)
      BIND (year(now()) - year(?dob) AS ?age)
      FILTER (?age >= 65)
      FILTER (?appointmentDate >= "2023-01-01"^^xsd:date)
      FILTER (?appointmentDate <= "2023-12-31"^^xsd:date)
    }
    ORDER BY ?appointmentDate
    """
    execute_query(q1, "1. Elderly patients (65+) with appointments this year")
    
    # Query 2: High-cost treatments in last quarter
    q2 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?treatment ?treatmentType ?cost ?treatmentDate ?patientName
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:treatmentDate ?treatmentDate .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:firstName ?patFirstName .
      ?patient hmo:lastName ?patLastName .
      BIND (CONCAT(?patFirstName, " ", ?patLastName) AS ?patientName)
      FILTER (?cost > 4000)
      FILTER (?treatmentDate >= "2023-01-01"^^xsd:date)
      FILTER (?treatmentDate <= "2023-03-31"^^xsd:date)
    }
    ORDER BY DESC(?cost)
    """
    execute_query(q2, "2. High-cost treatments (>$4000) in Q1 2023")
    
    # Query 3: Patients allergic to specific medications
    q3 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?allergy ?currentMedication
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:allergicTo ?allergy .
      OPTIONAL {
        ?patient hmo:currentMedication ?currentMedication .
      }
    }
    ORDER BY ?lastName ?firstName
    """
    execute_query(q3, "3. Patients with medication allergies")
    
    # Query 4: Average length of stay by diagnosis
    q4 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?diagnosis (AVG(?lengthStay) as ?avgLength)
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:primaryDiagnosis ?diagnosis .
      ?patient hmo:lengthOfStay ?lengthStay .
    }
    GROUP BY ?diagnosis
    ORDER BY DESC(?avgLength)
    """
    execute_query(q4, "4. Average length of stay by diagnosis")
    
    # Query 5: Patients with multiple chronic conditions
    q5 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName 
           (COUNT(?condition) as ?conditionCount) 
           (GROUP_CONCAT(?condition; SEPARATOR=", ") as ?conditions)
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:hasMedicalCondition ?condition .
    }
    GROUP BY ?patient ?firstName ?lastName
    HAVING (COUNT(?condition) > 1)
    ORDER BY DESC(?conditionCount)
    """
    execute_query(q5, "5. Patients with multiple chronic conditions (comorbidities)")
    
    # Query 6: Diabetes treatments and medications
    q6 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?treatmentType ?medication ?treatmentDate
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:primaryDiagnosis "Diabetes" .
      ?patient hmo:undergoesTreatment ?treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:treatmentDate ?treatmentDate .
      OPTIONAL {
        ?treatment hmo:usesMedication ?medication .
      }
    }
    ORDER BY ?treatmentDate
    """
    execute_query(q6, "6. Treatments for diabetic patients")
    
    # Query 7: Follow-up appointments after surgery
    q7 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?surgeryDate ?followupDate ?doctor
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?surgery a hmo:Treatment .
      ?surgery hmo:treatmentType "Surgery" .
      ?surgery hmo:treatmentDate ?surgeryDate .
      ?surgery hmo:isResultOf ?surgeryAppt .
      ?surgeryAppt hmo:isAppointmentOf ?patient .
      ?followup a hmo:Appointment .
      ?followup hmo:reasonForVisit "Follow-up" .
      ?followup hmo:appointmentDate ?followupDate .
      ?followup hmo:isAppointmentOf ?patient .
      ?followup hmo:supervisedBy ?doctor .
      FILTER (?followupDate > ?surgeryDate)
    }
    ORDER BY DESC(?surgeryDate)
    """
    execute_query(q7, "7. Follow-up appointments after surgical procedures")
    
    # Query 8: Hospital ward occupancy status
    q8 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?ward ?totalBeds ?occupiedBeds ?availableBeds
           ((?occupiedBeds / ?totalBeds * 100) as ?occupancyRate)
    WHERE {
      ?ward a hmo:HospitalWard .
      ?ward hmo:totalBeds ?totalBeds .
      ?ward hmo:occupiedBeds ?occupiedBeds .
      BIND (?totalBeds - ?occupiedBeds AS ?availableBeds)
    }
    ORDER BY DESC(?occupancyRate)
    """
    execute_query(q8, "8. Current occupancy status of hospital wards")

def run_medical_staff_queries():
    """Medical Staff & Specialization Queries"""
    print("\n" + "="*100)
    print("MEDICAL STAFF & SPECIALIZATION QUERIES")
    print("="*100)
    
    # Query 9: Oncology specialists with >15 years experience
    q9 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?doctor ?firstName ?lastName ?specialization ?yearsExperience ?hospital
    WHERE {
      ?doctor a hmo:Doctor .
      ?doctor hmo:firstName ?firstName .
      ?doctor hmo:lastName ?lastName .
      ?doctor hmo:hasSpecialization ?specialization .
      ?doctor hmo:yearsExperience ?yearsExperience .
      ?doctor hmo:worksAt ?hospital .
      FILTER (regex(?specialization, "Oncology", "i"))
      FILTER (?yearsExperience > 15)
    }
    ORDER BY DESC(?yearsExperience)
    """
    execute_query(q9, "9. Oncology specialists with >15 years experience")
    
    # Query 10: Doctors available by hospital branch
    q10 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?hospital ?doctor ?firstName ?lastName ?specialization
    WHERE {
      ?doctor a hmo:Doctor .
      ?doctor hmo:firstName ?firstName .
      ?doctor hmo:lastName ?lastName .
      ?doctor hmo:hasSpecialization ?specialization .
      ?doctor hmo:worksAt ?hospital .
      ?doctor hmo:isAvailable true .
    }
    ORDER BY ?hospital ?specialization ?lastName
    """
    execute_query(q10, "10. Available doctors by hospital branch")
    
    # Query 11: Specialization distribution across branches
    q11 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?hospital ?specialization (COUNT(?doctor) as ?doctorCount)
    WHERE {
      ?doctor a hmo:Doctor .
      ?doctor hmo:hasSpecialization ?specialization .
      ?doctor hmo:worksAt ?hospital .
    }
    GROUP BY ?hospital ?specialization
    ORDER BY ?hospital ?specialization
    """
    execute_query(q11, "11. Specialization distribution across hospital branches")
    
    # Query 12: Senior doctors supervising appointments
    q12 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?doctor ?firstName ?lastName ?yearsExperience ?appointmentCount
    WHERE {
      ?doctor a hmo:SeniorDoctor .
      ?doctor hmo:firstName ?firstName .
      ?doctor hmo:lastName ?lastName .
      ?doctor hmo:yearsExperience ?yearsExperience .
      ?appointment hmo:supervisedBy ?doctor .
      BIND (COUNT(?appointment) AS ?appointmentCount)
    }
    GROUP BY ?doctor ?firstName ?lastName ?yearsExperience
    ORDER BY DESC(?appointmentCount)
    """
    execute_query(q12, "12. Senior doctors and their appointment load")

def run_administrative_queries():
    """Administrative & Operational Queries"""
    print("\n" + "="*100)
    print("ADMINISTRATIVE & OPERATIONAL QUERIES")
    print("="*100)
    
    # Query 13: Missed appointments (no-shows)
    q13 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?appointmentDate ?reason ?doctor
    WHERE {
      ?appointment a hmo:NoShowAppointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?appointment hmo:appointmentDate ?appointmentDate .
      ?appointment hmo:reasonForVisit ?reason .
      ?appointment hmo:supervisedBy ?doctor .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
    }
    ORDER BY DESC(?appointmentDate)
    """
    execute_query(q13, "13. Patients who missed scheduled appointments (no-shows)")
    
    # Query 14: Most common reasons for visits
    q14 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?reason (COUNT(?appointment) as ?visitCount)
    WHERE {
      ?appointment a hmo:Appointment .
      ?appointment hmo:reasonForVisit ?reason .
    }
    GROUP BY ?reason
    ORDER BY DESC(?visitCount)
    """
    execute_query(q14, "14. Most common reasons for patient visits")
    
    # Query 15: Cancelled appointments and reasons
    q15 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?appointmentDate ?reason ?cancelledBy
    WHERE {
      ?appointment a hmo:CancelledAppointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?appointment hmo:appointmentDate ?appointmentDate .
      ?appointment hmo:reasonForVisit ?reason .
      ?appointment hmo:cancelledBy ?cancelledBy .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
    }
    ORDER BY DESC(?appointmentDate)
    """
    execute_query(q15, "15. Cancelled appointments and cancellation reasons")
    
    # Query 16: Appointment distribution patterns
    q16 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?dayOfWeek ?timeSlot (COUNT(?appointment) as ?appointmentCount)
    WHERE {
      ?appointment a hmo:Appointment .
      ?appointment hmo:appointmentDate ?date .
      ?appointment hmo:appointmentTime ?time .
      BIND (xsd:string(?date) AS ?dateStr)
      BIND (substr(?dateStr, 1, 10) AS ?dateOnly)
      BIND (if(?time < "12:00:00"^^xsd:time, "Morning", 
              if(?time < "17:00:00"^^xsd:time, "Afternoon", "Evening")) AS ?timeSlot)
      BIND (dayname(?date) AS ?dayOfWeek)
    }
    GROUP BY ?dayOfWeek ?timeSlot
    ORDER BY ?dayOfWeek ?timeSlot
    """
    execute_query(q16, "16. Appointment distribution by day and time slot")

def run_financial_queries():
    """Financial & Billing Queries"""
    print("\n" + "="*100)
    print("FINANCIAL & BILLING QUERIES")
    print("="*100)
    
    # Query 17: Average treatment cost by specialty
    q17 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?specialization (AVG(?cost) as ?avgCost) (COUNT(?treatment) as ?treatmentCount)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:supervisedBy ?doctor .
      ?doctor hmo:hasSpecialization ?specialization .
    }
    GROUP BY ?specialization
    ORDER BY DESC(?avgCost)
    """
    execute_query(q17, "17. Average treatment cost by medical specialty")
    
    # Query 18: Insurance coverage for treatments
    q18 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?insuranceProvider ?treatmentType 
           (COUNT(?treatment) as ?treatmentCount) 
           (AVG(?cost) as ?avgCost)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:hasInsurance ?insuranceProvider .
    }
    GROUP BY ?insuranceProvider ?treatmentType
    ORDER BY ?insuranceProvider ?treatmentType
    """
    execute_query(q18, "18. Insurance coverage analysis by treatment type")
    
    # Query 19: Delinquent payment accounts
    q19 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?patient ?firstName ?lastName ?billAmount ?dueDate ?daysOverdue
    WHERE {
      ?bill a hmo:DelinquentAccount .
      ?bill hmo:isGeneratedBy ?treatment .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?bill hmo:amount ?billAmount .
      ?bill hmo:dueDate ?dueDate .
      BIND (days(now() - ?dueDate) AS ?daysOverdue)
      FILTER (?daysOverdue > 90)
    }
    ORDER BY DESC(?daysOverdue)
    """
    execute_query(q19, "19. Patients with delinquent payment accounts (>90 days)")
    
    # Query 20: Revenue projections by department
    q20 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?department (SUM(?cost) as ?totalRevenue) (COUNT(?treatment) as ?treatmentCount)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:supervisedBy ?doctor .
      ?doctor hmo:worksAt ?hospital .
      ?hospital hmo:department ?department .
    }
    GROUP BY ?department
    ORDER BY DESC(?totalRevenue)
    """
    execute_query(q20, "20. Revenue projections by department")

def run_data_integration_queries():
    """Data Integration & Reasoning Queries"""
    print("\n" + "="*100)
    print("DATA INTEGRATION & REASONING QUERIES")
    print("="*100)
    
    # Query 21: Treatments exceeding insurance limits
    q21 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?treatmentType ?cost ?insuranceLimit ?coverageGap
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:hasInsurance ?insurance .
      ?insurance hmo:coverageLimit ?insuranceLimit .
      BIND (?cost - ?insuranceLimit AS ?coverageGap)
      FILTER (?cost > ?insuranceLimit)
    }
    ORDER BY DESC(?coverageGap)
    """
    execute_query(q21, "21. Treatments exceeding insurance coverage limits")
    
    # Query 22: High-cost treatments by insurance type
    q22 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?insuranceProvider ?treatmentType 
           (COUNT(?treatment) as ?highCostCount) 
           (AVG(?cost) as ?avgCost)
    WHERE {
      ?treatment a hmo:HighCostTreatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:hasInsurance ?insuranceProvider .
    }
    GROUP BY ?insuranceProvider ?treatmentType
    ORDER BY ?insuranceProvider DESC(?avgCost)
    """
    execute_query(q22, "22. High-cost treatments analysis by insurance type")
    
    # Query 23: Doctor success rates (simplified)
    q23 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?doctor ?firstName ?lastName ?specialization
           (COUNT(?treatment) as ?totalTreatments)
           (SUM(?successScore) as ?totalSuccess)
           ((SUM(?successScore) / COUNT(?treatment)) as ?successRate)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:successScore ?successScore .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:supervisedBy ?doctor .
      ?doctor hmo:firstName ?firstName .
      ?doctor hmo:lastName ?lastName .
      ?doctor hmo:hasSpecialization ?specialization .
    }
    GROUP BY ?doctor ?firstName ?lastName ?specialization
    HAVING (COUNT(?treatment) >= 5)
    ORDER BY DESC(?successRate)
    """
    execute_query(q23, "23. Doctor treatment success rates (based on success scores)")
    
    # Query 24: Treatment-recovery time correlation
    q24 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?treatmentType 
           (AVG(?recoveryDays) as ?avgRecoveryTime)
           (AVG(?cost) as ?avgCost)
           (COUNT(?treatment) as ?sampleSize)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:recoveryPeriod ?recoveryDays .
    }
    GROUP BY ?treatmentType
    HAVING (COUNT(?treatment) >= 3)
    ORDER BY ?avgRecoveryTime
    """
    execute_query(q24, "24. Treatment types and average recovery times")

def run_operational_efficiency_queries():
    """Operational Efficiency Queries"""
    print("\n" + "="*100)
    print("OPERATIONAL EFFICIENCY QUERIES")
    print("="*100)
    
    # Query 25: Patient satisfaction by hospital branch
    q25 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?hospital 
           (AVG(?satisfactionScore) as ?avgSatisfaction)
           (COUNT(?feedback) as ?feedbackCount)
    WHERE {
      ?feedback a hmo:PatientFeedback .
      ?feedback hmo:satisfactionScore ?satisfactionScore .
      ?feedback hmo:forHospital ?hospital .
    }
    GROUP BY ?hospital
    ORDER BY DESC(?avgSatisfaction)
    """
    execute_query(q25, "25. Patient satisfaction scores by hospital branch")
    
    # Query 26: Resource utilization rates
    q26 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?department ?equipmentType 
           (COUNT(?usage) as ?usageCount)
           (AVG(?duration) as ?avgUsageDuration)
    WHERE {
      ?usage a hmo:EquipmentUsage .
      ?usage hmo:equipmentType ?equipmentType .
      ?usage hmo:usageDuration ?duration .
      ?usage hmo:inDepartment ?department .
    }
    GROUP BY ?department ?equipmentType
    ORDER BY ?department DESC(?usageCount)
    """
    execute_query(q26, "26. Resource utilization rates by department and equipment")
    
    # Query 27: Cost-effective treatment protocols
    q27 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?condition ?treatmentProtocol 
           (AVG(?cost) as ?avgCost)
           (AVG(?successScore) as ?avgSuccess)
           (AVG(?recoveryDays) as ?avgRecovery)
           ((AVG(?successScore) / AVG(?cost) * 1000) as ?costEffectiveness)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:successScore ?successScore .
      ?treatment hmo:recoveryPeriod ?recoveryDays .
      ?treatment hmo:forCondition ?condition .
      ?treatment hmo:treatmentProtocol ?treatmentProtocol .
    }
    GROUP BY ?condition ?treatmentProtocol
    HAVING (COUNT(?treatment) >= 5)
    ORDER BY DESC(?costEffectiveness)
    """
    execute_query(q27, "27. Cost-effective treatment protocols by condition")
    
    # Query 28: Peak hours for medical services
    q28 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?serviceType ?hour (COUNT(?appointment) as ?appointmentCount)
    WHERE {
      ?appointment a hmo:Appointment .
      ?appointment hmo:appointmentTime ?time .
      ?appointment hmo:reasonForVisit ?serviceType .
      BIND (hours(?time) AS ?hour)
    }
    GROUP BY ?serviceType ?hour
    ORDER BY ?serviceType ?hour
    """
    execute_query(q28, "28. Peak hours analysis for different medical services")

def run_swrl_validation_queries():
    """SWRL Rule Validation Queries"""
    print("\n" + "="*100)
    print("SWRL RULE VALIDATION QUERIES")
    print("="*100)
    
    # Query 29: Elderly patients classification
    q29 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?age
    WHERE {
      ?patient a hmo:ElderlyPatient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:dateOfBirth ?dob .
      BIND (year(now()) - year(?dob) AS ?age)
    }
    ORDER BY DESC(?age)
    """
    execute_query(q29, "29. Patients classified as 'Elderly' by SWRL rules")
    
    # Query 30: Senior doctors classification
    q30 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?doctor ?firstName ?lastName ?yearsExperience
    WHERE {
      ?doctor a hmo:SeniorDoctor .
      ?doctor hmo:firstName ?firstName .
      ?doctor hmo:lastName ?lastName .
      ?doctor hmo:yearsExperience ?yearsExperience .
    }
    ORDER BY DESC(?yearsExperience)
    """
    execute_query(q30, "30. Doctors classified as 'Senior' by SWRL rules")
    
    # Query 31: High-cost treatments classification
    q31 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?treatment ?treatmentType ?cost ?treatmentDate
    WHERE {
      ?treatment a hmo:HighCostTreatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:cost ?cost .
      ?treatment hmo:treatmentDate ?treatmentDate .
    }
    ORDER BY DESC(?cost)
    """
    execute_query(q31, "31. Treatments classified as 'High-Cost' by SWRL rules")
    
    # Query 32: Delinquent accounts classification
    q32 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?bill ?patient ?firstName ?lastName ?amount ?dueDate ?daysOverdue
    WHERE {
      ?bill a hmo:DelinquentAccount .
      ?bill hmo:isGeneratedBy ?treatment .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?bill hmo:amount ?amount .
      ?bill hmo:dueDate ?dueDate .
      BIND (days(now() - ?dueDate) AS ?daysOverdue)
    }
    ORDER BY DESC(?daysOverdue)
    """
    execute_query(q32, "32. Bills classified as 'Delinquent Accounts' by SWRL rules")

def run_inference_testing_queries():
    """Inference Testing Queries"""
    print("\n" + "="*100)
    print("INFERENCE TESTING QUERIES")
    print("="*100)
    
    # Query 33: Medication allergy conflicts
    q33 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName ?allergy ?prescribedMedication ?treatmentDate
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:allergicTo ?allergy .
      ?treatment hmo:usesMedication ?prescribedMedication .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      ?treatment hmo:treatmentDate ?treatmentDate .
      FILTER (regex(?prescribedMedication, ?allergy, "i"))
    }
    ORDER BY ?patient ?treatmentDate
    """
    execute_query(q33, "33. Potential medication allergy conflicts")
    
    # Query 34: Doctor-patient specialty matching
    q34 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?patientName ?condition ?doctor ?doctorName ?specialization ?matchQuality
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?patFirst .
      ?patient hmo:lastName ?patLast .
      ?patient hmo:primaryDiagnosis ?condition .
      ?doctor a hmo:Doctor .
      ?doctor hmo:firstName ?docFirst .
      ?doctor hmo:lastName ?docLast .
      ?doctor hmo:hasSpecialization ?specialization .
      BIND (CONCAT(?patFirst, " ", ?patLast) AS ?patientName)
      BIND (CONCAT(?docFirst, " ", ?docLast) AS ?doctorName)
      BIND (if(regex(?specialization, ?condition, "i"), "Perfect Match", 
              if(bound(?specialization), "Specialist Available", "General Care")) AS ?matchQuality)
    }
    ORDER BY ?matchQuality ?patientName
    """
    execute_query(q34, "34. Doctor-patient specialty matching analysis")
    
    # Query 35: Equipment availability alternatives
    q35 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?treatment ?requiredEquipment ?alternativeEquipment ?hospital ?availability
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:requiresEquipment ?requiredEquipment .
      ?alternative hmo:alternativeFor ?requiredEquipment .
      ?alternative hmo:equipmentType ?alternativeEquipment .
      ?alternative hmo:locatedAt ?hospital .
      ?alternative hmo:isAvailable ?availability .
    }
    ORDER BY ?requiredEquipment ?hospital
    """
    execute_query(q35, "35. Equipment alternatives for treatments")

def run_quality_assurance_queries():
    """Quality Assurance Queries"""
    print("\n" + "="*100)
    print("QUALITY ASSURANCE QUERIES")
    print("="*100)
    
    # Query 36: Conflicting medication allergies
    q36 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName (COUNT(?allergy) as ?allergyCount)
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      ?patient hmo:allergicTo ?allergy .
    }
    GROUP BY ?patient ?firstName ?lastName
    HAVING (COUNT(?allergy) > 3)
    ORDER BY DESC(?allergyCount)
    """
    execute_query(q36, "36. Patients with multiple medication allergies")
    
    # Query 37: Appointment data completeness
    q37 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?appointment ?hasPatient ?hasDoctor ?hasDate ?hasTime ?hasReason
           (if(?hasPatient && ?hasDoctor && ?hasDate && ?hasTime && ?hasReason, "Complete", "Incomplete") as ?status)
    WHERE {
      ?appointment a hmo:Appointment .
      BIND (bound(?patient) AS ?hasPatient)
      BIND (bound(?doctor) AS ?hasDoctor)
      BIND (bound(?date) AS ?hasDate)
      BIND (bound(?time) AS ?hasTime)
      BIND (bound(?reason) AS ?hasReason)
      OPTIONAL { ?appointment hmo:isAppointmentOf ?patient }
      OPTIONAL { ?appointment hmo:supervisedBy ?doctor }
      OPTIONAL { ?appointment hmo:appointmentDate ?date }
      OPTIONAL { ?appointment hmo:appointmentTime ?time }
      OPTIONAL { ?appointment hmo:reasonForVisit ?reason }
    }
    ORDER BY ?status
    LIMIT 20
    """
    execute_query(q37, "37. Appointment data completeness check")
    
    # Query 38: Treatments without cost information
    q38 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?treatment ?treatmentType ?treatmentDate ?patient
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      ?treatment hmo:treatmentDate ?treatmentDate .
      ?treatment hmo:isResultOf ?appointment .
      ?appointment hmo:isAppointmentOf ?patient .
      FILTER NOT EXISTS { ?treatment hmo:cost ?cost }
    }
    ORDER BY ?treatmentDate
    """
    execute_query(q38, "38. Treatments missing cost information")
    
    # Query 39: Insurance claims validation
    q39 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?claim ?patient ?treatment ?hasTreatmentRecord ?hasCost ?isValid
           (if(?hasTreatmentRecord && ?hasCost, "Valid", "Invalid") as ?validationStatus)
    WHERE {
      ?claim a hmo:InsuranceClaim .
      ?claim hmo:forPatient ?patient .
      ?claim hmo:forTreatment ?treatment .
      BIND (bound(?treatmentRecord) AS ?hasTreatmentRecord)
      BIND (bound(?cost) AS ?hasCost)
      BIND (?hasTreatmentRecord && ?hasCost AS ?isValid)
      OPTIONAL { 
        ?treatment hmo:cost ?cost .
        ?treatment a hmo:Treatment .
      }
    }
    ORDER BY ?validationStatus
    """
    execute_query(q39, "39. Insurance claims validation against treatment records")

def run_completeness_validation_queries():
    """Completeness Validation Queries"""
    print("\n" + "="*100)
    print("COMPLETENESS VALIDATION QUERIES")
    print("="*100)
    
    # Query 40: Patient record completeness
    q40 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?patient ?firstName ?lastName 
           (if(bound(?dob), 1, 0) as ?hasDOB 
           (if(bound(?contact), 1, 0) as ?hasContact 
           (if(bound(?address), 1, 0) as ?hasAddress 
           (if(bound(?insurance), 1, 0) as ?hasInsurance 
           ((?hasDOB + ?hasContact + ?hasAddress + ?hasInsurance) / 4.0 * 100) as ?completenessScore)
    WHERE {
      ?patient a hmo:Patient .
      ?patient hmo:firstName ?firstName .
      ?patient hmo:lastName ?lastName .
      OPTIONAL { ?patient hmo:dateOfBirth ?dob }
      OPTIONAL { ?patient hmo:contactNumber ?contact }
      OPTIONAL { ?patient hmo:address ?address }
      OPTIONAL { ?patient hmo:hasInsurance ?insurance }
    }
    ORDER BY ?completenessScore
    LIMIT 15
    """
    execute_query(q40, "40. Patient demographic information completeness")
    
    # Query 41: Medical specialization coverage
    q41 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?specialization (COUNT(?doctor) as ?doctorCount) 
           (if(?doctorCount > 0, "Covered", "Not Covered") as ?coverageStatus)
    WHERE {
      ?specialization a hmo:MedicalSpecialization .
      OPTIONAL {
        ?doctor hmo:hasSpecialization ?specialization .
      }
    }
    GROUP BY ?specialization
    ORDER BY ?coverageStatus ?doctorCount
    """
    execute_query(q41, "41. Medical specialization coverage analysis")
    
    # Query 42: Treatment classification completeness
    q42 = """
    PREFIX hmo: <http://www.semanticweb.org/healthcare-ontology#>
    SELECT ?treatment ?treatmentType 
           (if(bound(?classification), "Classified", "Unclassified") as ?classificationStatus)
           (if(bound(?protocol), "Protocol Defined", "No Protocol") as ?protocolStatus)
    WHERE {
      ?treatment a hmo:Treatment .
      ?treatment hmo:treatmentType ?treatmentType .
      OPTIONAL { ?treatment hmo:treatmentClassification ?classification }
      OPTIONAL { ?treatment hmo:treatmentProtocol ?protocol }
    }
    ORDER BY ?classificationStatus ?protocolStatus
    LIMIT 20
    """
    execute_query(q42, "42. Treatment classification and protocol completeness")

def main():
    """Main function to execute all SPARQL queries"""
    print("HOSPITAL MANAGEMENT ONTOLOGY - SPARQL VALIDATION SUITE")
    print("="*100)
    print("Repository: https://github.com/BadrHsnAltahir/Hospital-Management-Ontology-Design-Pattern")
    print("="*100)
    
    # Execute all query categories
    run_clinical_queries()
    run_medical_staff_queries()
    run_administrative_queries()
    run_financial_queries()
    run_data_integration_queries()
    run_operational_efficiency_queries()
    run_swrl_validation_queries()
    run_inference_testing_queries()
    run_quality_assurance_queries()
    run_completeness_validation_queries()
    
    print("\n" + "="*100)
    print("VALIDATION COMPLETE - All 42 competency questions executed")
    print("="*100)
    
    # Summary statistics
    total_triples = len(g)
    classes = len(set(g.subjects(RDF.type, OWL.Class)))
    properties = len(set(g.subjects(RDF.type, OWL.ObjectProperty))) + len(set(g.subjects(RDF.type, OWL.DatatypeProperty)))
    individuals = len(set(g.subjects(RDF.type, None))) - classes - properties
    
    print(f"\nONTOLOGY SUMMARY STATISTICS:")
    print(f"Total Triples: {total_triples}")
    print(f"Classes: {classes}")
    print(f"Properties: {properties}") 
    print(f"Individuals: {individuals}")
    print(f"Queries Executed: 42")
    print(f"Validation Status: COMPLETE")

if __name__ == "__main__":
    main()