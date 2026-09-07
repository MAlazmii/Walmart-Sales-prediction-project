from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import joblib
import csv
import numpy as np
import os
import math

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}}) 


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server address
app.config['MAIL_PORT'] = 587  # Replace with your SMTP server port
app.config['MAIL_USE_TLS'] = True  # Replace with True or False depending on your SMTP server
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('SMTP_SENDER', os.environ.get('SMTP_USERNAME'))
app.config['MAIL_USERNAME'] = os.environ.get('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP_PASSWORD')  # Configure outside source control

mail = Mail(app)

# Get the current directory
current_directory = os.path.dirname(os.path.realpath(__file__))

# Load the pre-trained model
model_path = os.path.join(current_directory, 'trained_model2.pkl')
model = joblib.load(model_path)


@app.route('/send-email', methods=['POST'])
def send_email():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight Request Handled'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.json

    email = data.get('email')
    prediction_data = data.get('predictionData')
    inventory_data = data.get('inventoryData')

    if not email:
        return jsonify({'error': 'Email address is required'}), 400

    # Construct email message
    msg = Message('Predictions and Inventory Data', recipients=[email])
    msg.body = f'''Dear User,

Thank you so much for visiting our site and using our prediction service. We truly appreciate your interest and trust in our platform.

Here are the predictions and inventory data you requested:

Prediction Data: {prediction_data}

Inventory Data:
{format_inventory_data(inventory_data)}

We hope this information is helpful to you. If you have any further questions or need assistance, please don't hesitate to contact us.

Thank you once again for choosing our platform.

Best regards,
Your Name
Your Position/Company Name'''

    try:
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

def format_inventory_data(inventory_data):
    formatted_data = ''
    for item in inventory_data:
        formatted_data += f"Store: {item['store']}, Dept: {item['dept']}, Date: {item['date']}, Is Holiday: {item['isHoliday']}, Inventory: {item['inventory']}\n"
    return formatted_data

# Define endpoint for prediction
@app.route('/predict', methods=['POST', 'OPTIONS'])

def predict():
    print(request)
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight Request Handled'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response


    # Get input values from the request
    input_data = request.json
    print(input_data)
    
    # Process input data and convert to array for prediction
    input_values = [
        input_data['Store'],
        input_data['Dept'],
        input_data['Temperature'],
        input_data['MarkDown1'],
        input_data['MarkDown2'],
        input_data['MarkDown4'],
        input_data['MarkDown5'],
        input_data['Size'],
        input_data['Type_A'],
        input_data['Type_B'],
        input_data['Type_C'],
        input_data['Month'],
        input_data['Day'],
        input_data['isHoliday']
    ]

    input_array = np.array([input_values])
    
    # Make prediction using the loaded model
    prediction = model.predict(input_array)
    prediction =  math.floor(prediction)
    
    
    # Return prediction as JSON response
    response = jsonify({'prediction': int(prediction)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response



def load_csv(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data    

# Route to handle API requests
@app.route('/get_data', methods=['GET', 'OPTIONS'])


def get_data():
    print(request)

    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight Request Handled'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response 
    
    store_number = request.args.get('store_number')
    dept_number = request.args.get('dept_number')

    # Check if store_number and dept_number are provided
    if not store_number or not dept_number:
        return jsonify({'error': 'Store number and department number are required parameters'})

    # Load CSV file
    csv_filename = 'test_with_last_known_inventory.csv'  # Change this to your CSV filename
    if not os.path.isfile(csv_filename):
        return jsonify({'error': 'CSV file not found'})

    # Load CSV data
    data = load_csv(csv_filename)

    # Search for data matching store_number and dept_number
    results = []
    for row in data:
        if row['Store'] == store_number and row['Dept'] == dept_number:
            results.append(row)

    # Return results in JSON format
            print(jsonify(results))
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

