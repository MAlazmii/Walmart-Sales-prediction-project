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
model = None  # Loaded only when prediction is requested.


@app.route('/send-email', methods=['POST'])
def send_email():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight Request Handled'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    email = data.get('email')
    prediction_data = data.get('predictionData')
    inventory_data = data.get('inventoryData')

    keys = {'store', 'dept', 'date', 'isHoliday', 'inventory'}
    if not isinstance(email, str) or '@' not in email or '\n' in email or '\r' in email:
        return jsonify({'error': 'A valid email address is required'}), 400
    if not isinstance(inventory_data, list) or any(
        not isinstance(item, dict) or not keys.issubset(item) for item in inventory_data
    ):
        return jsonify({'error': 'Inventory records are required as a list'}), 400

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
        return jsonify({'error': 'Email delivery failed; check SMTP configuration'}), 503

def format_inventory_data(inventory_data):
    formatted_data = ''
    for item in inventory_data:
        formatted_data += f"Store: {item['store']}, Dept: {item['dept']}, Date: {item['date']}, Is Holiday: {item['isHoliday']}, Inventory: {item['inventory']}\n"
    return formatted_data

# Define endpoint for prediction
@app.route('/predict', methods=['POST', 'OPTIONS'])

def predict():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight Request Handled'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response


    input_data = request.get_json(silent=True)
    fields = ['Store', 'Dept', 'Temperature', 'MarkDown1', 'MarkDown2',
              'MarkDown4', 'MarkDown5', 'Size', 'Type_A', 'Type_B', 'Type_C',
              'Month', 'Day', 'isHoliday']
    try:
        if not isinstance(input_data, dict):
            raise ValueError('A JSON object is required')
        values = {key: float(input_data[key]) for key in fields}
        if not all(math.isfinite(value) for value in values.values()):
            raise ValueError('Features must be finite numbers')
        for key, low, high in [('Store', 1, 45), ('Dept', 1, 99),
                               ('Month', 1, 12), ('Day', 1, 31)]:
            if not values[key].is_integer() or not low <= values[key] <= high:
                raise ValueError('Invalid ' + key)
        flags = [values[key] for key in ['Type_A', 'Type_B', 'Type_C']]
        if any(value not in (0, 1) for value in flags) or sum(flags) != 1:
            raise ValueError('Choose exactly one store type')
        if values['isHoliday'] not in (0, 1) or values['Size'] <= 0:
            raise ValueError('Invalid holiday flag or store size')
    except (KeyError, TypeError, ValueError, OverflowError):
        return jsonify({'error': 'Provide all valid numeric features and exactly one store type'}), 400

    global model
    try:
        if model is None:
            model = joblib.load(model_path)
        prediction_values = np.asarray(model.predict(np.array([[values[key] for key in fields]]))).reshape(-1)
        if prediction_values.size != 1 or not np.isfinite(prediction_values[0]):
            raise ValueError('Model returned an invalid prediction')
        prediction = math.floor(float(prediction_values[0]))
    except Exception:
        return jsonify({'error': 'Prediction unavailable; check the model environment'}), 503

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
        return jsonify({'error': 'Store number and department number are required parameters'}), 400

    # Load CSV file
    csv_filename = os.path.join(current_directory, 'test_with_last_known_inventory.csv')  # Change this to your CSV filename
    if not os.path.isfile(csv_filename):
        return jsonify({'error': 'CSV file not found'}), 503

    # Load CSV data
    data = load_csv(csv_filename)

    # Search for data matching store_number and dept_number
    results = []
    for row in data:
        if row['Store'] == store_number and row['Dept'] == dept_number:
            results.append(row)

    # Return results in JSON format
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

