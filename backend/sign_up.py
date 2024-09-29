import hashlib

def sign_up(connection, username, password, user_type):
    cursor = connection.cursor()

    # Hash the password before storing it
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        # Check if the username already exists
        check_user_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        cursor.execute(check_user_query, (username,))
        (user_count,) = cursor.fetchone()

        if user_count > 0:
            return "Error: Username already exists. Please choose a different username."

        # SQL query to insert a new user
        sign_up_query = "INSERT INTO users (users_id, password, user_type) VALUES (%s, %s, %s)"
        sign_up_data = (username, hashed_password, user_type)

        cursor.execute(sign_up_query, sign_up_data)
        connection.commit()
        return "User signed up successfully."

    except Exception as e:
        connection.rollback()
        # You might want to log the error here
        print(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

    finally:
        cursor.close()

if __name__ == '__main__':
    from sql_connection import get_sql_connection

    connection = get_sql_connection()
    print(sign_up(connection, 'Ma Tara Stores', 'joymatara1234', 'retailer'))

