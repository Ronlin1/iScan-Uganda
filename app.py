from flask import Flask, request, jsonify

app = Flask(__name__)

# Dictionary to store product information
product_info_storage = {}

@app.route('/process-scan', methods=['POST'])
def process_scan():
    data = request.json
    product_info = data.get('info', '')

    # Save the product information in a dictionary
    product_id = len(product_info_storage) + 1
    product_info_storage[product_id] = product_info

    return jsonify({'message': 'Product information received', 'product_id': product_id})

@app.route('/get-product-info/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    product_info = product_info_storage.get(product_id, 'Product not found')
    return jsonify({'product_info': product_info})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
