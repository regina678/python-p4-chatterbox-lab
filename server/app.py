from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([m.to_dict() for m in messages]), 200

    if request.method == 'POST':
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({'error': 'Missing body or username'}), 400

        message = Message(body=body, username=username)
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get_or_404(id)

    if request.method == 'PATCH':
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']
            message.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(message.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(port=5000)
