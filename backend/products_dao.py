from sql_connection import get_sql_connection
from datetime import date

def get_all_products(connection):
    cursor = connection.cursor()
    query = ("SELECT products.id, products.name, products.price_per_unit, uom_table.uom_name, products.quantity_of_uom, products.category, products.exp_date, products.shelf_num, products.picture_of_the_prod, products.description "
             "FROM products "
             "INNER JOIN uom_table ON products.uom_id = uom_table.uom_id;")
    cursor.execute(query)
    response = []
    for (id, name, price_per_unit, uom_name, quantity_of_uom, category, exp_date, shelf_num, picture_of_the_prod, description) in cursor:
        response.append({
            'product_id': id,
            'name': name,
            'price_per_unit': price_per_unit,
            'uom_name': uom_name,
            'quantity_of_uom': quantity_of_uom,
            'category': category,
            'exp_date': exp_date,
            'shelf_num': shelf_num,
            'picture_of_the_prod': picture_of_the_prod,
            'description': description
        })
    return response


def insert_new_product(connection, product, user_id):
    cursor = connection.cursor()
    query = ("INSERT INTO products "
             "(name, uom_id, price_per_unit, quantity_of_uom, category, exp_date, shelf_num, picture_of_the_prod, description, user_id) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = (
        product['name'],
        product['uom_id'],
        product['price_per_unit'],
        product['quantity_of_uom'],
        product['category'],
        product['exp_date'],
        product['shelf_num'],
        product['picture_of_the_prod'],
        product['description'],
        user_id  # Adding the user_id to the insert query
    )

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid


def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = "DELETE FROM products WHERE id = %s"
    cursor.execute(query, (product_id,))
    connection.commit()

    return product_id  # Return the deleted product ID directly



def edit_product(connection, product_id, updated_product):
    cursor = connection.cursor()
    query = ("UPDATE products SET "
             "name = %s, "
             "price_per_unit = %s, "
             "quantity_of_uom = %s, "
             "category = %s, "
             "shelf_num = %s, "
             "description = %s "
             "WHERE id = %s")

    data = (
        updated_product['name'],
        updated_product['price_per_unit'],
        updated_product['quantity_of_uom'],
        updated_product['category'],
        updated_product['shelf_num'],
        updated_product['description'],
        product_id
    )

    cursor.execute(query, data)
    connection.commit()

    return cursor.rowcount


def add_cart_products(connection, cart_id, user_id):
    cursor = connection.cursor()

    # Query to fetch products from cart and join with products_manu using product_id
    query = ("""
        SELECT p.name, p.uom_id, p.price_per_unit, p.quantity_of_uom, p.category, 
               p.exp_date, p.shelf_num, p.picture_of_the_prod, p.description, c.quantity
        FROM cart_manu c
        JOIN products_manu p ON c.product_id = p.id
        WHERE c.cart_id = %s
    """)

    cursor.execute(query, (cart_id,))
    products_in_cart = cursor.fetchall()  # Fetch all products in the cart

    inserted_or_updated_product_ids = []  # To store inserted or updated product IDs

    # Loop through all products fetched from the cart
    for product in products_in_cart:
        product_data = {
            'name': product[0],
            'uom_id': product[1],
            'price_per_unit': product[2],
            'quantity_of_uom': product[3],
            'category': product[4],
            'exp_date': product[5],
            'shelf_num': product[6],
            'picture_of_the_prod': product[7],
            'description': product[8],
            'quantity': product[9]  # Quantity from cart
        }

        # Validation: Check if the product with the same name already exists in the 'products' table
        check_query = "SELECT id, quantity_of_uom FROM products WHERE name = %s"
        cursor.execute(check_query, (product_data['name'],))
        existing_product = cursor.fetchone()

        if existing_product:
            # Product exists, update the quantity
            product_id = existing_product[0]
            existing_quantity = existing_product[1]
            new_quantity = existing_quantity + product_data['quantity']

            # Update the quantity of the existing product
            update_query = "UPDATE products SET quantity_of_uom = %s WHERE id = %s"
            cursor.execute(update_query, (new_quantity, product_id))
            print(f"Updated product '{product_data['name']}' with new quantity: {new_quantity}")

            # Append the product ID to the list
            inserted_or_updated_product_ids.append(product_id)
        else:
            # Insert the new product since it doesn't exist
            new_product_id = insert_new_product(connection, product_data, user_id)
            print(f"Inserted new product '{product_data['name']}' with ID: {new_product_id}")

            # Append the new product ID to the list
            inserted_or_updated_product_ids.append(new_product_id)

    connection.commit()  # Commit the changes after inserting/updating all products

    return inserted_or_updated_product_ids



if __name__ == '__main__':
    connection = get_sql_connection()
    print(get_all_products(connection))
    print(insert_new_product(connection, {
        'name': "Aspirin",
        'uom_id': 1,
        'price_per_unit': 50,
        'quantity_of_uom': 100,
        'category': 'fever',
        'exp_date': date(2025, 4, 19),
        'shelf_num': 4,
        'description': 'description'
    }))




    # delete_product(connection, 3)