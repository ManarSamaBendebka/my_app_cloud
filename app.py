from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

application = Flask(__name__)
CORS(application)

application.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://my_db_zezb_user:63CA58pGd6Wj1cIdQMhuc2JZT5zNssiC@dpg-d09aqc3ipnbc73a6alj0-a.oregon-postgres.render.com/my_db_zezb'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_instance = SQLAlchemy(application)

class Person(db_instance.Model):
    uid = db_instance.Column(db_instance.Integer, primary_key=True)
    full_name = db_instance.Column(db_instance.String(100), nullable=False)
    email_address = db_instance.Column(db_instance.String(120), nullable=False, unique=True)

with application.app_context():
    db_instance.create_all()

@application.route('/')
def main_page():
    return render_template('index.html')

@application.route('/api/users', methods=['GET'])
def fetch_users():
    keyword = request.args.get('q', '')
    if keyword:
        records = Person.query.filter(
            (Person.full_name.ilike(f"%{keyword}%")) | 
            (Person.email_address.ilike(f"%{keyword}%"))
        ).all()
    else:
        records = Person.query.all()
    return jsonify([{'id': p.uid, 'name': p.full_name, 'email': p.email_address} for p in records])

@application.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_entry = Person(full_name=data['name'], email_address=data['email'])
    db_instance.session.add(new_entry)
    db_instance.session.commit()
    return jsonify({'id': new_entry.uid, 'name': new_entry.full_name, 'email': new_entry.email_address}), 201

@application.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    person = Person.query.get(user_id)
    if not person:
        return jsonify({'error': 'Not found'}), 404
    person.full_name = data['name']
    person.email_address = data['email']
    db_instance.session.commit()
    return jsonify({'id': person.uid, 'name': person.full_name, 'email': person.email_address})

@application.route('/api/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    person = Person.query.get(user_id)
    if not person:
        return jsonify({'error': 'Not found'}), 404
    db_instance.session.delete(person)
    db_instance.session.commit()
    return jsonify({'result': 'Deleted'})

if __name__ == '__main__':
    application.run(debug=True)
