# Walmart Sales Prediction Web Application

This project is a web application built using Flask, HTML, CSS, and JavaScript. It provides a user interface for predicting weekly sales and checking inventory levels based on user input.

## Features

- **Sales Prediction**: Users can input various parameters such as store number, department number, temperature, markdowns, size, type, month, day, and holiday status to predict weekly sales.
- **Inventory Check**: Users can select a store and department to check inventory levels.
- **Email Notification**: Users can input their email address to receive predictions and inventory data via email.

## Installation

1. Clone the repository:

    ```bash
    git clone https:
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask server:

    ```bash
    python flask_model_server.py
    ```

4. Open `index.html` in your web browser.

## Usage

### Sales Prediction

1. Fill in the required fields in the prediction form.
2. Click the "Predict" button.
3. View the predicted weekly sales in the "Predictions" section.

### Inventory Check

1. Select a store from the dropdown menu.
2. Select a department from the dropdown menu.
3. Click the "Check Inventory" button.
4. View inventory data in the "Inventory Levels" section.

### Email Notification

1. Enter your email address in the email form.
2. Perform a sales prediction or inventory check.
3. Click the "Send Email" button to receive predictions and inventory data via email.

## File Structure

- **flask_model_server.py**: Flask application for handling API requests and predictions.
- **index.html**: HTML file containing the user interface elements.
- **scripts.js**: JavaScript file containing client-side functionality.
- **styles.css**: CSS file for styling the web application.

## Contributing

Contributions are welcome! If you have any suggestions or find any issues, please open an issue or a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project was inspired by the need for a simple web interface for predicting sales and checking inventory.

