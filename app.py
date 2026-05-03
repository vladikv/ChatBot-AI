from functools import wraps
from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
import re
import mysql.connector

app = Flask(__name__)


API_KEY = os.getenv("APP_API_KEY", "secret-key-123")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "orders_db",
}


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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/chat", methods=["POST"])
@require_api_key
def chat():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Send JSON in format {'message': 'text'}"}), 400

    message = data.get("message").strip()

    cancel_match = re.search(r'cancel(?:.*?)order\s+(\d+)|order\s+(\d+).*?cancel', message, re.IGNORECASE)
    if cancel_match:
        order_id = cancel_match.group(1) or cancel_match.group(2)
        result = cancel_order(order_id)
        if "success" in result:
            return jsonify({"response": f"Order {order_id} has been successfully cancelled."})
        return jsonify({"response": result["error"]})

    if re.search(r'all orders|list orders|show orders', message, re.IGNORECASE):
        orders = get_all_orders()
        if not orders:
            return jsonify({"response": "No orders found."})
        lines = [f"Order {o['order_id']}: {o['status']}" for o in orders]
        return jsonify({"response": "\n".join(lines)})

    words = message.split()
    for word in words:
        clean_word = re.sub(r'\D', '', word)
        if clean_word:
            order = get_order_status(clean_word)
            if order:
                return jsonify({"response": f"Order {clean_word} status: {order['status']}"})

    return jsonify({"response": ask_ai(message)})


if __name__ == "__main__":
    app.run(debug=True)
 