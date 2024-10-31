from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import sqlite3
from textblob import TextBlob
import speech_recognition as sr
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    with app.app_context():
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sentiment REAL
            )
        ''')
        conn.commit()

# Home route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle creating journal entries
@app.route('/entries', methods=['POST'])
def create_entry():
    content = request.json.get('content')
    if not content:
        return jsonify({"error": "Content is required"}), 400

    sentiment = TextBlob(content).sentiment.polarity
    timestamp = datetime.now().isoformat()
    conn = get_db_connection()
    conn.execute('INSERT INTO entries (content, timestamp, sentiment) VALUES (?, ?, ?)',
                 (content, timestamp, sentiment))
    conn.commit()
    conn.close()

    return jsonify({"message": "Entry created", "sentiment": sentiment}), 201

# Route to retrieve all journal entries
@app.route('/entries', methods=['GET'])
def get_entries():
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries').fetchall()
    conn.close()
    return jsonify([dict(entry) for entry in entries])

# Route to handle getting or deleting a specific entry by ID
@app.route('/entries/<int:id>', methods=['GET', 'DELETE'])
def handle_entry(id):
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM entries WHERE id = ?', (id,)).fetchone()

    if request.method == 'GET':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404
        return jsonify(dict(entry))

    elif request.method == 'DELETE':
        if entry is None:
            return jsonify({"error": "Entry not found"}), 404
        conn.execute('DELETE FROM entries WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Entry deleted"}), 200

# Route to handle audio transcription
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
            return jsonify({"transcription": transcription}), 200
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Speech recognition error: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)





