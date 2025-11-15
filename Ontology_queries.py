# -*- coding: utf-8 -*-
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
import datetime

# الخطوة 1: تحميل الأنطولوجيا من الملف
# Step 1: Load the ontology from the file
g = Graph()
g.parse("HospitalManagementOntologyDesignPattern.xml", format="xml") # Here but ontology file directory

print("✅ تم تحميل الأنطولوجيا بنجاح | Ontology loaded successfully")
print(f"📊 عدد البيانات الثلاثية: {len(g)} | Number of triples: {len(g)}\n")

# تعريف النامسبيس
# Define namespaces
HODP = Namespace("http://www.semanticweb.org/healthcare-ontology#")

# الاستعلام 1: الحصول على جميع الأطباء المخضرمين (خبرة > 15 سنة)
# Query 1: Get all senior doctors (experience > 15 years)
query1 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?doctor ?firstName ?lastName ?specialization ?yearsExperience ?hospital
WHERE {
    ?doctor rdf:type hodp:Doctor .
    ?doctor hodp:firstName ?firstName .
    ?doctor hodp:lastName ?lastName .
    ?doctor hodp:hasSpecialization ?spec .
    ?spec rdfs:label ?specialization .
    ?doctor hodp:yearsExperience ?yearsExperience .
    ?doctor hodp:worksAt ?hospital .
    FILTER (?yearsExperience > 15)
}
ORDER BY DESC(?yearsExperience)
"""

print("👨‍⚕️ الاستعلام 1: الأطباء المخضرمين (خبرة > 15 سنة)")
print("Query 1: Senior Doctors (experience > 15 years)")
print("-" * 70)

results1 = g.query(query1)
for row in results1:
    print(f"الطبيب: {row.firstName} {row.lastName}")
    print(f"التخصص: {row.specialization}")
    print(f"سنوات الخبرة: {row.yearsExperience}")
    print(f"مكان العمل: {row.hospital.split('#')[1]}")
    print("-" * 50)

print(f"📈 العدد الإجمالي: {len(results1)} طبيب مخضرم\n")

# الاستعلام 2: العلاجات عالية التكلفة (تكلفة > 2000)
# Query 2: High cost treatments (cost > 2000)
query2 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?treatment ?treatmentType ?description ?cost ?treatmentDate ?patient
WHERE {
    ?treatment rdf:type hodp:Treatment .
    ?treatment hodp:treatmentType ?treatmentType .
    ?treatment hodp:description ?description .
    ?treatment hodp:cost ?cost .
    ?treatment hodp:treatmentDate ?treatmentDate .
    ?treatment hodp:isResultOf ?appointment .
    ?appointment hodp:isAppointmentOf ?patient .
    FILTER (?cost > 2000)
}
ORDER BY DESC(?cost)
"""

print("💰 الاستعلام 2: العلاجات عالية التكلفة (أكثر من 2000)")
print("Query 2: High Cost Treatments (more than 2000)")
print("-" * 70)

results2 = g.query(query2)
total_high_cost = 0
for row in results2:
    print(f"نوع العلاج: {row.treatmentType}")
    print(f"الوصف: {row.description}")
    print(f"التكلفة: ${float(row.cost):.2f}")
    print(f"تاريخ العلاج: {row.treatmentDate}")
    print(f"المريض: {row.patient.split('#')[1]}")
    total_high_cost += float(row.cost)
    print("-" * 50)

print(f"💵 إجمالي تكلفة العلاجات عالية التكلفة: ${total_high_cost:.2f}\n")

# الاستعلام 3: تحليل المواعيد حسب الحالة
# Query 3: Appointment analysis by status
query3 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?status (COUNT(?appointment) as ?count)
WHERE {
    ?appointment rdf:type hodp:Appointment .
    ?appointment hodp:status ?status .
}
GROUP BY ?status
ORDER BY DESC(?count)
"""

print("📅 الاستعلام 3: تحليل المواعيد حسب الحالة")
print("Query 3: Appointment Analysis by Status")
print("-" * 70)

results3 = g.query(query3)
total_appointments = 0
for row in results3:
    print(f"الحالة: {row.status} - العدد: {row.count}")
    total_appointments += int(row.count)

print(f"📊 إجمالي عدد المواعيد: {total_appointments}")

# حساب معدل الإلغاء وعدم الحضور
cancel_query = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT (COUNT(?appointment) as ?problemCount)
WHERE {
    ?appointment rdf:type hodp:Appointment .
    ?appointment hodp:status ?status .
    FILTER (?status = "Cancelled" || ?status = "No-show")
}
"""

problem_results = g.query(cancel_query)
problem_count = int(list(problem_results)[0].problemCount)
problem_rate = (problem_count / total_appointments) * 100 if total_appointments > 0 else 0

print(f"⚠️  معدل المشاكل (إلغاء/عدم حضور): {problem_rate:.1f}%\n")

# الاستعلام 4: توزيع المرضى حسب مزودي التأمين
# Query 4: Patient distribution by insurance providers
query4 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?insuranceProvider (COUNT(?patient) as ?patientCount)
WHERE {
    ?patient rdf:type hodp:Patient .
    ?patient hodp:hasInsurance ?provider .
    ?provider rdfs:label ?insuranceProvider .
}
GROUP BY ?insuranceProvider
ORDER BY DESC(?patientCount)
"""

print("🏥 الاستعلام 4: توزيع المرضى حسب مزودي التأمين")
print("Query 4: Patient Distribution by Insurance Providers")
print("-" * 70)

results4 = g.query(query4)
for row in results4:
    print(f"مزود التأمين: {row.insuranceProvider} - عدد المرضى: {row.patientCount}")

print()

# الاستعلام 5: الأطباء حسب التخصص والمكان
# Query 5: Doctors by specialization and location
query5 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?specialization ?hospital (COUNT(?doctor) as ?doctorCount)
WHERE {
    ?doctor rdf:type hodp:Doctor .
    ?doctor hodp:hasSpecialization ?spec .
    ?spec rdfs:label ?specialization .
    ?doctor hodp:worksAt ?hospital .
}
GROUP BY ?specialization ?hospital
ORDER BY ?specialization DESC(?doctorCount)
"""

print("🎯 الاستعلام 5: توزيع الأطباء حسب التخصص والمستشفى")
print("Query 5: Doctor Distribution by Specialization and Hospital")
print("-" * 70)

results5 = g.query(query5)
for row in results5:
    hospital_name = row.hospital.split('#')[1] if '#' in row.hospital else row.hospital
    print(f"التخصص: {row.specialization} - المستشفى: {hospital_name} - عدد الأطباء: {row.doctorCount}")

print()

# الاستعلام 6: العلاجات الأكثر شيوعاً وتكلفتها المتوسطة
# Query 6: Most common treatments and their average cost
query6 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?treatmentType (COUNT(?treatment) as ?count) (AVG(?cost) as ?avgCost) (SUM(?cost) as ?totalCost)
WHERE {
    ?treatment rdf:type hodp:Treatment .
    ?treatment hodp:treatmentType ?treatmentType .
    ?treatment hodp:cost ?cost .
}
GROUP BY ?treatmentType
ORDER BY DESC(?count)
"""

print("🩺 الاستعلام 6: تحليل العلاجات (التكرار والتكلفة)")
print("Query 6: Treatment Analysis (Frequency and Cost)")
print("-" * 70)

results6 = g.query(query6)
for row in results6:
    avg_cost = float(row.avgCost) if row.avgCost else 0
    total_cost = float(row.totalCost) if row.totalCost else 0
    print(f"نوع العلاج: {row.treatmentType}")
    print(f"عدد المرات: {row.count} - متوسط التكلفة: ${avg_cost:.2f} - إجمالي التكلفة: ${total_cost:.2f}")
    print("-" * 50)

# الاستعلام 7: المرضى المسنين (عمر > 65 سنة)
# Query 7: Elderly patients (age > 65 years)
query7 = """
PREFIX hodp: <http://www.semanticweb.org/healthcare-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?patient ?firstName ?lastName ?dateOfBirth ?age ?insurance
WHERE {
    ?patient rdf:type hodp:Patient .
    ?patient hodp:firstName ?firstName .
    ?patient hodp:lastName ?lastName .
    ?patient hodp:dateOfBirth ?dateOfBirth .
    ?patient hodp:hasInsurance ?insurance .
    
    BIND (year(now()) - year(?dateOfBirth) AS ?age)
    FILTER (?age > 65)
}
ORDER BY DESC(?age)
"""

print("👵 الاستعلام 7: المرضى المسنين (عمر > 65 سنة)")
print("Query 7: Elderly Patients (age > 65 years)")
print("-" * 70)

results7 = g.query(query7)
for row in results7:
    insurance_name = row.insurance.split('#')[1] if '#' in row.insurance else row.insurance
    print(f"المريض: {row.firstName} {row.lastName}")
    print(f"تاريخ الميلاد: {row.dateOfBirth} - العمر: {row.age} سنة")
    print(f"مزود التأمين: {insurance_name}")
    print("-" * 50)

print(f"👥 عدد المرضى المسنين: {len(results7)}")

print("\n🎉 اكتملت جميع الاستعلامات بنجاح! | All queries completed successfully!")
