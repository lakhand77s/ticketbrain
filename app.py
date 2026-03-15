import os
from flask import Flask, render_template, request, jsonify
from database import get_db, init_db
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

init_db()
@app.route('/')
def index():
    conn = get_db()
    tickets = conn.execute(
        'SELECT * FROM tickets ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    tickets = [dict(t) for t in tickets]
    return render_template('index.html', tickets=tickets)

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    data = request.json
    summary = generate_summary(data)
    conn = get_db()
    conn.execute('''
        INSERT INTO tickets 
        (ticket_no, subject, type, priority, status, module, description, ai_summary, created_at, is_requirement)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['ticket_no'],
        data['subject'],
        data['type'],
        data['priority'],
        data['status'],
        data['module'],
        data['description'],
        summary,
        datetime.now().strftime('%d-%m-%Y %H:%M'),
        data.get('is_requirement', False)
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'summary': summary})

@app.route('/approve/<int:ticket_id>', methods=['POST'])
def approve_ticket(ticket_id):
    conn = get_db()
    conn.execute('UPDATE tickets SET approved = 1 WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/reject/<int:ticket_id>', methods=['POST'])
def reject_ticket(ticket_id):
    conn = get_db()
    conn.execute('UPDATE tickets SET approved = 0 WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/delete/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    conn = get_db()
    conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

def generate_summary(data):
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        prompt = "Summarize this ticket for a CEO in 2-3 lines. Ticket: " + str(data['subject']) + " Type: " + str(data['type']) + " Module: " + str(data['module']) + " Description: " + str(data['description'])
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text
    except Exception:
        return str(data['subject']) + " — " + str(data['type']) + " ticket in " + str(data['module']) + " module. Priority: " + str(data['priority']) + "."

def create_app():
    init_db()
    return app

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)