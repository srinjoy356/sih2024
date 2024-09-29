from sql_connection import get_sql_connection
from datetime import date


def add_products_to_cart(connection, cart_id, products):
    """
    Add multiple products to the cart or update their quantities if they already exist.

    connection: Database connection object.
    cart_id: Unique ID for the cart.
    products: List of dictionaries containing product_id and quantity.
    Number of rows affected (inserted/updated).
    """
    cursor = connection.cursor()

    query = """
        INSERT INTO cart_manu (cart_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = VALUES(quantity);
    """
    # Prepare data as a list of tuples
    data = [(cart_id, product['product_id'], product['quantity']) for product in products]

    try:
        cursor.executemany(query, data)  # Execute the query for all products at once
        connection.commit()
        return cursor.rowcount  # Return the number of affected rows
    except Exception as e:
        connection.rollback()
        return str(e)  # Return the error message if something goes wrong


def get_cart_products(connection, cart_id):
    """
    Fetch all products in a specific cart.

    connection: Database connection object.
    cart_id: Unique ID for the cart.
    List of products in the cart.
    """
    cursor = connection.cursor()

    query = """
        SELECT p.id AS product_id, p.name, p.price_per_unit, c.quantity, (p.price_per_unit * c.quantity) AS total_price
        FROM cart_manu c
        JOIN products_manu p ON c.product_id = p.id
        WHERE c.cart_id = %s
    """

    try:
        cursor.execute(query, (cart_id,))
        products = cursor.fetchall()
        return products
    except Exception as e:
        return str(e)  # Return error message if something goes wrong


def get_all_cart_manu(connection):
    cursor = connection.cursor()

    # Updated query to fetch product details per cart_id
    query = ("SELECT cart_manu.cart_id, cart_manu.product_id, cart_manu.quantity, products_manu.price_per_unit "
             "FROM cart_manu "
             "INNER JOIN products_manu ON cart_manu.product_id = products_manu.id "
             "ORDER BY cart_manu.cart_id;")

    cursor.execute(query)

    response = {}

    # Fetch the cart details and group products by cart_id
    for (cart_id, product_id, quantity, price_per_unit) in cursor:
        if cart_id not in response:
            response[cart_id] = {
                'cart_id': cart_id,
                'products': []
            }

        response[cart_id]['products'].append({
            'product_id': product_id,
            'quantity': quantity,
            'price_per_unit': price_per_unit
        })

    return list(response.values())


def delete_cart(connection, cart_id):
    cursor = connection.cursor()
    query = "DELETE FROM cart_manu WHERE cart_id = %s"
    cursor.execute(query, (cart_id,))
    connection.commit()

    return cart_id  # Return the deleted cart ID directly


if __name__ == '__main__':
    connection = get_sql_connection()
    # print(add_products_to_cart(connection, 1, [
    #     {
    #         'product_id':2,
    #         'quantity': 10
    #     },
    #     {
    #         'product_id': 3,
    #         'quantity': 10
    #     }
    # ]))
    print(get_cart_products(connection, 1))