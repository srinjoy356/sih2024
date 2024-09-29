import qrcode
import json
import io
import base64

def generate_qr_code(cart_id, receivers_addressW, receivers_addressR, date, distance, price_per_unit):
    # Create a dictionary to store the data
    qr_data = {
        'cart_id': cart_id,
        'recivers_addressW': receivers_addressW,
        'recivers_addressR': receivers_addressR,
        'Date': date,
        'Distance': distance,
        'Price_per_Unit': price_per_unit
    }

    # Convert the dictionary to a JSON formatted string
    qr_data_json = json.dumps(qr_data)

    # Generate the QR code
    img = qrcode.make(qr_data_json)

    # Convert the image to binary data using a BytesIO object
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)  # Reset stream position to the beginning

    return img_byte_arr

#Example usage
# print(generate_qr_code(
#     cart_id='06',
#     receivers_addressW='0xf39fd6e5laad88f6f4ce6ab8827279cfffb92266',
#     receivers_addressR='0xc123',
#     date='2024-09-20',
#     distance='32 km',
#     price_per_unit='100'
# ))
