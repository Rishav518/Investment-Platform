from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)

#Name of Database we use in this project
DATABASE = "user_accounts.db"


def create_table():
    #Creating table for new user
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL NOT NULL
            )
            """
        )

@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    #Fetching name from Client
    name = data.get("name")
    #Fetching balance from Client
    balance = data.get("balance")
    if not name or not balance:
        return jsonify({"error": "Name and balance are required."}), 400
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (name, balance))
        conn.commit()
    return jsonify({"message": "Account created successfully. "}), 200



if __name__ == "__main__":
    create_table()
    app.run(debug=True)
