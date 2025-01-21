from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app)

# Fungsi untuk koneksi ke database SQLite
def get_db_connection():
    connection = sqlite3.connect('tasks.db')
    connection.row_factory = sqlite3.Row  # Agar hasil query berupa dictionary
    return connection

# Endpoint untuk inisialisasi database
@app.route('/init-db', methods=['GET'])
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()
    return jsonify({"message": "Database initialized successfully!"})

# Endpoint untuk menambahkan task baru
@app.route('/add-tasks', methods=['POST'])  # Mengganti /tasks menjadi /add-tasks
def add_task():
    data = request.get_json()  # Ambil data dari body request (JSON)
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )
    connection.commit()
    connection.close()

    return jsonify({"message": "Task added successfully"}), 201

# Endpoint untuk melihat semua task
@app.route('/tasks', methods=['GET'])
def get_tasks():
    connection = get_db_connection()
    cursor = connection.cursor()
    tasks = cursor.execute("SELECT * FROM tasks").fetchall()
    connection.close()

    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks_list)

# Endpoint untuk memperbarui task berdasarkan ID
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    done = data.get('done')

    connection = get_db_connection()
    cursor = connection.cursor()

    # Periksa apakah task dengan ID tersebut ada
    task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        connection.close()
        return jsonify({"error": "Task not found"}), 404

    # Update task
    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, done = ?
        WHERE id = ?
    """, (title, description, done, task_id))
    connection.commit()
    connection.close()

    return jsonify({"message": "Task updated successfully"})

# Endpoint untuk menghapus task berdasarkan ID
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Periksa apakah task dengan ID tersebut ada
    task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        connection.close()
        return jsonify({"error": "Task not found"}), 404

    # Hapus task
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    connection.close()

    return jsonify({"message": "Task deleted successfully"})

# Jalankan server Flask
if __name__ == '__main__':
    app.run(debug=True)
