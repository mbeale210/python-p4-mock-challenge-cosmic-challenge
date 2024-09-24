#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET'])
def get_scientists():
    scientists = Scientist.query.all()
    return jsonify([{"id": s.id, "name": s.name, "field_of_study": s.field_of_study} for s in scientists]), 200

@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist(id):
    scientist = db.session.get(Scientist, id)
    if scientist:
        return jsonify(scientist.to_dict(rules=('missions',))), 200
    return jsonify({"error": "Scientist not found"}), 404

@app.route('/scientists', methods=['POST'])
def create_scientist():
    data = request.json
    try:
        scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
        db.session.add(scientist)
        db.session.commit()
        return jsonify(scientist.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    data = request.json
    try:
        for attr in ['name', 'field_of_study']:
            if attr in data:
                setattr(scientist, attr, data[attr])
        db.session.commit()
        return jsonify(scientist.to_dict()), 202
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    db.session.delete(scientist)
    db.session.commit()
    return '', 204, {'Content-Type': 'application/json'}

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "distance_from_earth": p.distance_from_earth,
        "nearest_star": p.nearest_star
    } for p in planets]), 200

@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.json
    try:
        mission = Mission(name=data['name'], scientist_id=data['scientist_id'], planet_id=data['planet_id'])
        db.session.add(mission)
        db.session.commit()
        return jsonify(mission.to_dict(rules=('scientist', 'planet'))), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)