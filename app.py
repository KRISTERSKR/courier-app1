from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import googlemaps
import os

app = Flask(__name__)

# Konfigurācija datubāzei (SQLite testēšanai)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deliveries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Google Maps API atslēga (Aizvieto ar savu atslēgu)
GOOGLE_MAPS_API_KEY = "TAVA_GOOGLE_MAPS_API_ATSLĒGA"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Datubāzes modelis kurjera izsaukumiem
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    pickup_address = db.Column(db.String(255), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)

# Mājaslapa (Frontend HTML fails)
@app.route('/')
def home():
    return render_template('index.html')

# API maršruts pieteikuma pievienošanai
@app.route('/request_delivery', methods=['POST'])
def request_delivery():
    data = request.json
    new_delivery = Delivery(
        client_name=data['client_name'],
        pickup_address=data['pickup_address'],
        delivery_address=data['delivery_address']
    )
    db.session.add(new_delivery)
    db.session.commit()
    return jsonify({"message": "Kurjera pieteikums veiksmīgi pieņemts!"}), 201

# API maršruts visu pieprasījumu iegūšanai
@app.route('/get_deliveries', methods=['GET'])
def get_deliveries():
    deliveries = Delivery.query.all()
    deliveries_list = [
        {
            "id": d.id,
            "client_name": d.client_name,
            "pickup_address": d.pickup_address,
            "delivery_address": d.delivery_address
        }
        for d in deliveries
    ]
    return jsonify(deliveries_list)

# API maršruts optimāla maršruta ģenerēšanai
@app.route('/generate_route', methods=['GET'])
def generate_route():
    deliveries = Delivery.query.all()
    waypoints = [d.pickup_address for d in deliveries] + [d.delivery_address for d in deliveries]

    if len(waypoints) < 2:
        return jsonify({"error": "Nav pietiekami daudz punktu maršruta ģenerēšanai"}), 400

    directions_result = gmaps.directions(
        origin=waypoints[0],
        destination=waypoints[-1],
        waypoints=waypoints[1:-1],
        optimize_waypoints=True,
        mode="driving"
    )

    return jsonify(directions_result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Inicializē datubāzi
    app.run(debug=True)
