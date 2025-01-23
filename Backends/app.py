from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Aktifkan CORS untuk semua route

# Function to connect to SQLite database
def get_db_connection():
    connection = sqlite3.connect('tasks.db')
    connection.row_factory = sqlite3.Row  # Return rows as dictionaries
    return connection

# Endpoint to initialize the database
@app.route('/add-tasks', methods=['POST'])
def add_task():
    data = request.get_json()  # Ambil data JSON dari request
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')

    # Validasi input
    if not title or not description or not deadline:
        return jsonify({"error": "Title, description, and deadline are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Masukkan data ke database
    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, deadline) VALUES (?, ?, ?)",
            (title, description, deadline)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()  # Rollback jika terjadi error
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

    return jsonify({"message": "Task added successfully"}), 201


# Endpoint to retrieve all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    connection = get_db_connection()
    cursor = connection.cursor()
    tasks = cursor.execute("SELECT * FROM tasks").fetchall()
    connection.close()

    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks_list)

# Endpoint to update a task by ID
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')  # Get deadline from request
    done = data.get('done')

    # Validate deadline format if provided
    try:
        if deadline:
            datetime.strptime(deadline, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if task exists
    task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        connection.close()
        return jsonify({"error": "Task not found"}), 404

    # Update task
    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, deadline = ?, done = ?
        WHERE id = ?
    """, (title, description, deadline, done, task_id))
    connection.commit()
    connection.close()

    return jsonify({"message": "Task updated successfully"})

# Endpoint to delete a task by ID
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if task exists
    task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        connection.close()
        return jsonify({"error": "Task not found"}), 404

    # Delete task
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    connection.close()

    return jsonify({"message": "Task deleted successfully"})

# Run Flask server
if __name__ == '__main__':
    app.run(debug=True)
