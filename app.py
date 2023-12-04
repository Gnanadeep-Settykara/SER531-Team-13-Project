from flask import Flask, render_template, request
import stardog
import pandas as pd

app = Flask(__name__)

# Set up the Stardog connection details
connection_details = {
    'endpoint': 'https://sd-5ef3ce14.stardog.cloud:5820',
    'username': 'tlam23@asu.edu',
    'password': 'Stardog@2022',
}

# Render the initial form
@app.route('/')
def health_form():
    return render_template('health_form.html')



# Handle the form submission route for patient details
@app.route("/submit_patient_form", methods=['POST'])
def patient_form():
    patient_id = request.form['patient_id']
    query = f'''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ont: <http://www.semanticweb.org/tlam23/ontologies/2023/11/Final#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?age ?gender ?bmi ?disease ?cure
    FROM <tag:stardog:api:context:all>
    WHERE {{
        ?patient rdf:type ont:Patient.
        ?patient ont:has_PatientId "{patient_id}"^^xsd:string.

        ?patient ont:has_Age ?age.
        ?patient ont:has_gender ?gender.
        ?patient ont:hasMedicalInfo ?healthStats.
        ?healthStats rdf:type ont:Health_Stats.
        ?healthStats ont:has_BMI ?bmi.

        ?patient ont:hasDisease ?disease.
        ?cure rdf:type ont:Cure.
        ?disease ont:hasCure ?cure.
    }}
    '''

    # Connect to Stardog and execute the query
    with stardog.Connection('Final_DB', **connection_details) as conn:
        results = conn.select(query)

    # Check if any records are found
    if not results['results']['bindings']:
        return render_template('submit_patient_form.html', results=[], not_found=True)

    # Process the results
    disease = results['results']['bindings'][0]['disease']['value'].split('tag:stardog:designer:Final_Project:data:Disease:')[1].replace('%20', ' ')
    gender = 'Male' if results['results']['bindings'][0]['gender']['value'] == '2' else 'Female'
    age = results['results']['bindings'][0]['age']['value']
    bmi = results['results']['bindings'][0]['bmi']['value']

    out_dict = [{'patient_Id': patient_id, 'Age': age, 'BMI': bmi, 'Gender': gender, 'Disease': disease}]
    return render_template('submit_patient_form.html', results=out_dict, not_found=False)


     


# Handle the form submission route
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get data from the form
    age = request.form['age']
    bmi = request.form['bmi']
    gender = request.form['gender']
    activity = request.form['activity']
    smoking = request.form['smoking']
    blood_pressure = request.form['bloodPressure']
    # health_condition = request.form['healthCondition']

    # Construct the query based on the form inputs
    query = f""" 


PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ont: <http://www.semanticweb.org/tlam23/ontologies/2023/11/Final#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?patient
FROM <tag:stardog:api:context:all>
WHERE {{
  ?patient rdf:type ont:Patient.
  ?patient ont:has_Age "{age}"^^xsd:int.
  ?patient ont:has_gender "{gender}"^^xsd:string.
  
  ?patient ont:hasMedicalInfo ?healthStats.
  ?healthStats rdf:type ont:Health_Stats.
  ?healthStats ont:has_BMI "{bmi}"^^xsd:int.
  ?healthStats ont:has_PhysicalActivity "{activity}"^^xsd:int.
  ?healthStats ont:has_SmokingHabit "{smoking}"^^xsd:int.
  ?healthStats ont:has_BloodPressure "{blood_pressure}"^^xsd:int.

}}
"""

    # Connect to Stardog and execute the query
    with stardog.Connection('Final_DB', **connection_details) as conn:
        results = conn.select(query)
    vals = results['results']['bindings']
    # print(vals)
    out = []
    out_dict = []
    for i in vals:
        out.append(i['patient']['value'].split('Patient:')[1])
        # Process the query results as needed
        # For example, fetch and process the patient data from results


    
    for patient_id in out:
        # print('hello')
        temp = {}
        temp['patient_id'] = patient_id
        query1 = f""" 

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ont: <http://www.semanticweb.org/tlam23/ontologies/2023/11/Final#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?cure ?description
    FROM <tag:stardog:api:context:all>
    WHERE {{
    ?patient rdf:type ont:Patient.
    ?patient ont:has_PatientId "{patient_id}"^^xsd:string.
    ?patient ont:hasPrecautions ?cure.
    ?cure ont:has_cure ?description.
    }}
    """
        
        results1 = conn.select(query1)
        out1 = results1['results']['bindings']
 

        temp['cure'] = out1[0]['description']['value']
        if temp['cure'].lower() == """Don't smoke. Have physical movement. Eat a heart-healthy diet. Maintain a healthy weight. Get quality sleep. Manage stress.""".lower():
            temp['Disease'] = "Cardiovascular disease"

        elif temp['cure'].lower() == """Follow a healthy lifestyle to prevent progression to diabetes. Adopt a balanced diet and engage in regular physical activity.""".lower():
            temp['Disease'] = 'Pre Diabetes'

        elif temp['cure'].lower() == """Follow prescribed treatment plan. Adopt a balanced diet and monitor carbohydrate intake. Engage in regular physical activity. Monitor blood sugar levels regularly.""".lower():
            temp['Disease'] = 'Diabetes'
        
        elif temp['cure'].lower() == """Maintaining a healthy weight. Eating healthy foods and drinks. Getting regular physical activity. Limiting alcohol consumption. Controlling blood pressure. Controlling diabetes. Checking cholesterol. Not smoking.""".lower():
            temp['Disease'] = 'Brain Stroke'

        else:
            temp['Disease'] = 'Healthy'
        
        out_dict.append(temp)
 
    # print(out_dict)
    return render_template('submit_health_form.html', results=out_dict)


if __name__ == '__main__':
    app.run(debug=True)
