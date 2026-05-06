from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import os
import re
import mysql.connector
import bcrypt
from google import genai

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-123")

API_KEY = os.getenv("APP_API_KEY", "secret-key-123")
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "orders_db",
}

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized. Provide a valid X-API-Key header."}), 401
        return f(*args, **kwargs)
    return decorated


def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in first."}), 401
        return f(*args, **kwargs)
    return decorated


def log_request(message, response, user_id=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (message, response, user_id) VALUES (%s, %s, %s)",
            (message, response, user_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")


def get_order_status(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"status": row[0]}
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None


def cancel_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"error": f"Order {order_id} not found."}
        if row[0] == "cancelled":
            conn.close()
            return {"error": f"Order {order_id} is already cancelled."}
        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        print(f"Database error: {e}")
        return {"error": str(e)}


def get_all_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, status FROM orders")
        rows = cursor.fetchall()
        conn.close()
        return [{"order_id": row[0], "status": row[1]} for row in rows]
    except Exception as e:
        print(f"Database error: {e}")
        return []


def ask_ai(message):
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )
        return response.text
    except Exception as e:
        return f"AI error: {str(e)}"


# --- Auth routes ---

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required."}), 400

    username = data["username"].strip()
    password = data["password"].strip()

    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty."}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Account created successfully."})
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required."}), 400

    username = data["username"].strip()
    password = data["password"].strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        conn.close()

        if not row or not bcrypt.checkpw(password.encode(), row[1].encode()):
            return jsonify({"error": "Invalid username or password."}), 401

        session["user_id"] = row[0]
        session["username"] = username
        return jsonify({"success": True, "username": username})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route('/me', methods=['GET'])
def me():
    if "user_id" in session:
        return jsonify({"logged_in": True, "username": session["username"]})
    return jsonify({"logged_in": False})


# --- Main routes ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/chat", methods=["POST"])
@require_api_key
@require_login
def chat():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Send JSON in format {'message': 'text'}"}), 400

    message = data.get("message").strip()
    user_id = session.get("user_id")
    response_text = ""

    cancel_match = re.search(r'cancel(?:.*?)order\s+(\d+)|order\s+(\d+).*?cancel', message, re.IGNORECASE)
    if cancel_match:
        order_id = cancel_match.group(1) or cancel_match.group(2)
        result = cancel_order(order_id)
        response_text = f"Order {order_id} has been successfully cancelled." if "success" in result else result["error"]
        log_request(message, response_text, user_id)
        return jsonify({"response": response_text})

    if re.search(r'all orders|list orders|show orders', message, re.IGNORECASE):
        orders = get_all_orders()
        response_text = "No orders found." if not orders else "\n".join([f"Order {o['order_id']}: {o['status']}" for o in orders])
        log_request(message, response_text, user_id)
        return jsonify({"response": response_text})

    words = message.split()
    for word in words:
        clean_word = re.sub(r'\D', '', word)
        if clean_word:
            order = get_order_status(clean_word)
            if order:
                response_text = f"Order {clean_word} status: {order['status']}"
                log_request(message, response_text, user_id)
                return jsonify({"response": response_text})

    response_text = ask_ai(message)
    log_request(message, response_text, user_id)
    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(debug=True)