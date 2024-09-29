from flask import Flask, request, jsonify, session, g, send_from_directory, send_file
from sql_connection import get_sql_connection
import mysql.connector
import json
import os
import uuid
import cv2
import io

import hashlib

import sign_up
import log_in
from pyzbar import pyzbar

import products_dao
import orders_dao
import uom_dao
from flask_cors import CORS
from submit import submit
# from bar_code_scanner import scan_barcodes
from qr_code_generator import generate_qr_code
from qr_code_scanner import scan_qr_codes
import products_manu_dao
import cart_manu_dao
from WEBSCRAPER import get_symptom_data, predict_medications, top_10_indian




app = Flask(__name__)

CORS(app)

app.secret_key = 'your_secret_key'

connection = get_sql_connection()

global_qr_data={}


#SQL connection
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='april@1904',
            database='drug_inventory'
        )
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#products retailer
@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = uom_dao.get_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getProducts', methods=['GET'])
def get_products():
    response = products_dao.get_all_products(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = json.loads(request.form['data'])
    user_id = request_payload.get('user_id')  # Extract the user_id from the request payload

    # Pass the user_id along with the product details to the insert_new_product function
    product_id = products_dao.insert_new_product(connection, request_payload, user_id)

    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/deleteProduct/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        return_id = products_dao.delete_product(connection, product_id)
        response = jsonify({
            'success': True,
            'product_id': return_id
        })
    except Exception as e:
        response = jsonify({
            'success': False,
            'error': str(e)
        })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




@app.route('/editProduct', methods=['POST'])
def edit_product():
    try:
        # Parse the JSON data sent in the POST request
        request_payload = json.loads(request.form['data'])

        # Extract the product_id and the updated product details from the payload
        product_id = request_payload['product_id']
        updated_product = {
            'name': request_payload['name'],
            'price_per_unit': request_payload['price_per_unit'],
            'quantity_of_uom': request_payload['quantity_of_uom'],
            'category': request_payload['category'],
            'shelf_num': request_payload['shelf_num'],
            'description': request_payload['description']
        }

        # Call the edit_product function from products_dao and pass the connection, product_id, and updated_product
        rows_affected = products_dao.edit_product(connection, product_id, updated_product)

        # Prepare the response indicating success or failure based on rows_affected
        response = jsonify({
            'success': rows_affected > 0,
            'rows_affected': rows_affected
        })

        # Allow cross-origin requests
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/addCartToProducts', methods=['POST'])
def add_cart_products_route():
    request_payload = request.json
    cart_id = request_payload.get('cart_id')  # Extract the cart_id from the request
    user_id = request_payload.get('user_id')  # Extract the user_id from the request

    # Call the add_cart_products function
    inserted_product_ids = products_dao.add_cart_products(connection, cart_id, user_id)

    response = jsonify({
        'inserted_product_ids': inserted_product_ids
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response





#Orders page


@app.route('/getAllOrders', methods=['GET'])
def get_all_orders():
    connection = get_db()
    response = orders_dao.get_all_orders(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/insertOrder', methods=['POST'])
def insert_order():
    request_payload = json.loads(request.form['data'])
    order_id = orders_dao.insert_order(connection, request_payload)
    response = jsonify({
        'order_id': order_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/updateOrder', methods=['POST'])
def update_order():
    request_payload = json.loads(request.form['data'])
    print(request_payload)
    order_id = request_payload['order_id']  # Ensure the order ID is included in the payload
    updated_order_id = orders_dao.update_order(connection, order_id, request_payload)
    response = jsonify({
        'order_id': updated_order_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


#log in and sign up page


@app.route('/login', methods=['POST'])
def login_route():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    # Input validation
    if not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_sql_connection()
    result = log_in.log_in(connection, username, password)

    if result['status'] == 'success':
        return jsonify({"message": "Login successful", "unique_user_id": result['unique_user_id']}), 200
    else:
        return jsonify({"error": result['message']}), 401



@app.route('/signup', methods=['POST'])
def signup_route():
    data = request.json

    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    # Input validation (you can add more checks here)
    if not username or not password or not user_type:
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_sql_connection()
    result = sign_up.sign_up(connection, username, password, user_type)

    if "Error" in result:
        return jsonify({"error": result}), 400
    else:
        return jsonify({"message": result}), 201


#OCR page


@app.route('/OCR')
def serve_index():
    # Serve the React app's index.html file
    return send_from_directory('../frontend/src/landing_page/warehouse', 'OCR.js')

@app.route('/<path:filename>')
def serve_static_file(filename):
    # Serve static files from the React app's build directory
    return send_from_directory('../frontend/src/landing_page/warehouse', filename)

@app.route('/extractFromDoc', methods=['POST'])
def extract_from_doc():
    file_format = request.form.get('file_format')
    file = request.files['file']

    # Save the uploaded file
    file_path = os.path.join("uploads", str(uuid.uuid4()) + ".pdf")
    file.save(file_path)

    # Call the submit function to extract the data
    data, error = submit(file_path, file_format)

    # Clean up the file after processing
    if os.path.exists(file_path):
        os.remove(file_path)

    if error:
        return jsonify({'status': 'error', 'message': error}), 500

    # Return the extracted data as a JSON response
    return jsonify({"message": data}), 201


# # Flask route to generate the QR code
# @app.route('/generate_qr', methods=['POST'])
# def generate_qr():
#     # Get data from the POST request
#     data = request.get_json()
#
#     # Extract the fields from the request
#     cart_id = data.get('cart_id')
#     receivers_addressW = data.get('receivers_addressW')
#     receivers_addressR = data.get('receivers_addressR')
#     date = data.get('date')
#     distance = data.get('distance')
#     price_per_unit = data.get('price_per_unit')
#     status = data.get('status')
#
#     # Generate the QR code using the data
#     filename = f"{cart_id}_QRCode.png"  # You can customize the filename if necessary
#     generate_qr_code(cart_id, receivers_addressW, receivers_addressR, date, distance, price_per_unit, status, filename)
#
#     # Return a JSON response with the file path or success message
#     return jsonify({"message": f"QR code saved as {filename}", "file": filename})




@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    # Get data from the POST request
    data = request.get_json()

    # Extract the fields from the request
    cart_id = data.get('cart_id')
    receivers_addressW = data.get('receivers_addressW')
    receivers_addressR = data.get('receivers_addressR')
    date = data.get('date')
    distance = data.get('distance')
    price_per_unit = data.get('price_per_unit')

    # Generate the QR code and get the binary image
    img_byte_arr = generate_qr_code(cart_id, receivers_addressW, receivers_addressR, date, distance, price_per_unit)

    # Send the binary data as an image file
    return send_file(img_byte_arr, mimetype='image/png')


#scan the qr code

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    # Predefined video stream URL
    url = "http://192.0.0.4:8080/video"

    # Call the QR code scanner
    qr_data = scan_qr_codes(url)
    global global_qr_data
    global_qr_data = qr_data


    if qr_data:
        return jsonify({"qr_data": qr_data}), 200
    else:
        return jsonify({"error": "No QR code detected or video stream error"}), 500


@app.route('/get_qr_data', methods=['GET'])
def get_qr_data():
    if global_qr_data:
        return jsonify({"qr_data": global_qr_data}), 200
    else:
        return jsonify({"error": "No QR data available"}), 404


#products_manu


@app.route('/getProductsManu', methods=['GET'])
def get_products_manu():
    response = products_manu_dao.get_all_products_manu(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/insertProductManu', methods=['POST'])
def insert_product_manu():
    request_payload = json.loads(request.form['data'])
    user_id = request_payload.get('user_id')  # Extract the user_id from the request payload

    # Pass the user_id along with the product details to the insert_new_product function
    product_id = products_manu_dao.insert_new_product_manu(connection, request_payload, user_id)

    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/deleteProductManu/<int:product_id>', methods=['DELETE'])
def delete_product_manu(product_id):

    connection = get_db()
    try:
        return_id = products_manu_dao.delete_product_manu(connection, product_id)
        response = jsonify({
            'success': True,
            'product_id': return_id
        })
    except Exception as e:
        response = jsonify({
            'success': False,
            'error': str(e)
        })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




@app.route('/editProductManu', methods=['POST'])
def edit_product_manu():
    try:
        # Parse the JSON data sent in the POST request
        request_payload = json.loads(request.form['data'])

        # Extract the product_id and the updated product details from the payload
        product_id = request_payload['product_id']
        updated_product = {
            'name': request_payload['name'],
            'price_per_unit': request_payload['price_per_unit'],
            'quantity_of_uom': request_payload['quantity_of_uom'],
            'category': request_payload['category'],
            'shelf_num': request_payload['shelf_num'],
            'description': request_payload['description']
        }

        # Call the edit_product function from products_dao and pass the connection, product_id, and updated_product
        rows_affected = products_manu_dao.edit_product_manu(connection, product_id, updated_product)

        # Prepare the response indicating success or failure based on rows_affected
        response = jsonify({
            'success': rows_affected > 0,
            'rows_affected': rows_affected
        })

        # Allow cross-origin requests
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json  # Receive JSON data from the frontend
    cart_id = data.get('cart_id')  # Extract cart_id from the request
    products = data.get('products')  # Extract the list of products

    if not cart_id or not products:
        return jsonify({"error": "Invalid data"}), 400

    # Add the products to the cart using the add_products_to_cart function
    result = cart_manu_dao.add_products_to_cart(connection, cart_id, products)

    if isinstance(result, str):  # If result is a string, it's an error
        return jsonify({"error": result}), 500

    return jsonify({"message": "Products added to cart successfully", "rows_affected": result}), 200


@app.route('/get_cart/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):

    # Fetch the products in the cart using the `get_cart_products` function
    products = cart_manu_dao.get_cart_products(connection, cart_id)

    if isinstance(products, str):  # If products is a string, it's an error message
        return jsonify({"error": products}), 500

    return jsonify({"cart_id": cart_id, "products": products}), 200


@app.route('/getCartsManu', methods=['GET'])
def get_cart_manu():
    connection= get_db()
    response = cart_manu_dao.get_all_cart_manu(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/deleteCartManu/<int:cart_id>', methods=['DELETE'])
def delete_cart_manu(cart_id):

    connection = get_db()
    try:
        return_id = cart_manu_dao.delete_cart(connection, cart_id)
        response = jsonify({
            'success': True,
            'cart_id': return_id
        })
    except Exception as e:
        response = jsonify({
            'success': False,
            'error': str(e)
        })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

#WEBSCRAPER

# Flask route to handle the prediction using web-scraped data
@app.route('/predict_medications', methods=['GET'])
def predict():
    try:
        # Get top symptoms based on web-scraped data
        top_symptoms_df = top_10_indian()
        top_symptoms = top_symptoms_df['symptoms'].tolist()  # List of symptoms

        # Predict medications based on top symptoms
        symptom_medications_map = predict_medications(top_symptoms)

        response = jsonify(symptom_medications_map)
        response.data = json.dumps(symptom_medications_map, indent=4)  # Pretty print with indentation
        return response, 200
    except KeyError as e:
        return jsonify({"error": f"Symptom not found: {e}"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/top_symptoms', methods=['GET'])
def get_top_symptoms():
    top_10_df = top_10_indian()

    # Directly convert DataFrame to JSON and return it
    return jsonify(top_10_df.to_dict(orient='records'))








if __name__ == "__main__":
    print("Starting Python Flask Server For Drug Inventory Management System")
    app.run(debug=True, port=5000)

