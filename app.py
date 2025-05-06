from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://my_db_zezb_user:63CA58pGd6Wj1cIdQMhuc2JZT5zNssiC@dpg-d09aqc3ipnbc73a6alj0-a.oregon-postgres.render.com/my_db_zezb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    query = request.args.get('q', '')
    if query:
        users = User.query.filter(
            (User.name.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        ).all()
    else:
        users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email} for u in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'name': new_user.name, 'email': new_user.email}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    user.name = data['name']
    user.email = data['email']
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': 'Deleted'})

if __name__ == '__main__':
    app.run(debug=True)
