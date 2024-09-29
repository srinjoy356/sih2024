from datetime import datetime
from sql_connection import get_sql_connection


def insert_order(connection, order):
    cursor = connection.cursor()

    # Insert into the orders_table
    order_query = ("INSERT INTO orders_table "
                   "(customer_name, total, date_time, phone_num, status)"
                   "VALUES (%s, %s, %s, %s, %s)")
    order_data = (order['customer_name'], order['grand_total'], datetime.now(), order['phone_num'], order['status'])

    # Execute the order query
    cursor.execute(order_query, order_data)

    # Get the last inserted ID
    order_id = cursor.lastrowid

    # Insert into order_details using a loop for each product
    order_details_query = ("INSERT INTO order_details "
                           "(order_id, product_id, quantity, total_price, price_per_unit) "
                           "SELECT %s, p.id, %s, %s, p.price_per_unit "
                           "FROM products p WHERE p.id = %s")

    for order_detail_record in order['order_details']:
        product_id = int(order_detail_record['product_id'])
        quantity = float(order_detail_record['quantity'])
        total_price = float(order_detail_record['total_price'])

        # Execute the query for each product in order details
        cursor.execute(order_details_query, (order_id, quantity, total_price, product_id))

    # Commit the transaction
    connection.commit()

    return order_id

def update_order(connection, order_id, order):
    cursor = connection.cursor()

    # Update the order in the orders_table
    update_order_query = ("UPDATE orders_table "
                          "SET customer_name = %s, total = %s, date_time = %s, phone_num = %s, status = %s "
                          "WHERE order_id = %s")
    update_order_data = (
        order['customer_name'],
        order['grand_total'],
        datetime.now(),
        order['phone_num'],
        order['status'],
        order_id
    )
    cursor.execute(update_order_query, update_order_data)

    # Update order details in order_details
    # First, delete the existing order details
    delete_order_details_query = "DELETE FROM order_details WHERE order_id = %s"
    cursor.execute(delete_order_details_query, (order_id,))

    # Insert the updated order details
    insert_order_details_query = ("INSERT INTO order_details "
                                  "(order_id, product_id, quantity, price) "
                                  "VALUES (%s, %s, %s, %s)")
    order_details_data = []
    for order_detail_record in order['order_details']:
        order_details_data.append([
            order_id,
            int(order_detail_record['product_id']),
            float(order_detail_record['quantity']),
            float(order_detail_record['total_price'])
        ])
    cursor.executemany(insert_order_details_query, order_details_data)

    connection.commit()
    return order_id


def get_order_details(connection, order_id):
    cursor = connection.cursor()

    query = "SELECT order_details.order_id, order_details.quantity, order_details.total_price, "\
            "products.name, products.price_per_unit FROM order_details LEFT JOIN products on " \
            "order_details.product_id = products.id where order_details.order_id = %s"

    data = (order_id, )

    cursor.execute(query, data)

    records = []
    for (order_id, quantity, total_price, product_name, price_per_unit) in cursor:
        records.append({
            'order_id': order_id,
            'quantity': quantity,
            'total_price': total_price,
            'product_name': product_name,
            'price_per_unit': price_per_unit
        })

    cursor.close()

    return records


def get_all_orders(connection):
    cursor = connection.cursor()
    query = ("SELECT * FROM orders_table")
    cursor.execute(query)
    column_names = [desc[0] for desc in cursor.description]
    print("Column Names:", column_names)
    response = []
    for (order_id, customer_name, date_time, phone_num, status, total, user_id) in cursor:
        response.append({
            'order_id': order_id,
            'customer_name': customer_name,
            'datetime': date_time,
            'phone_num': phone_num,
            'status': status,
            'total': total,
            'user_id': user_id
        })

    cursor.close()

    # append order details in each order
    for record in response:
        record['order_details'] = get_order_details(connection, record['order_id'])

    return response

if __name__ == '__main__':
    connection = get_sql_connection()
    print(get_all_orders(connection))
    # print(get_order_details(connection,4))
    # print(insert_order(connection, {
    #     'customer_name': 'dhaval',
    #     'total': '500',
    #     'datetime': datetime.now(),
    #     'order_details': [
    #         {
    #             'product_id': 1,
    #             'quantity': 2,
    #             'total_price': 50
    #         },
    #         {
    #             'product_id': 3,
    #             'quantity': 1,
    #             'total_price': 30
    #         }
    #     ]
    # }))