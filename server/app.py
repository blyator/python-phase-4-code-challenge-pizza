#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):

        restaurants = Restaurant.query.all()
        restaurants_data = []
        for restaurant in restaurants:
            restaurants_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address
            })
        return restaurants_data, 200


class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')
            
            if price is None or pizza_id is None or restaurant_id is None:
                return {'errors': ['validation errors']}, 400
        
            if not (1 <= price <= 30):
                return {'errors': ['validation errors']}, 400
            
            restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
            pizza = Pizza.query.filter_by(id=pizza_id).first()
            
            if not restaurant:
                return {'errors': ['validation errors']}, 400
            if not pizza:
                return {'errors': ['validation errors']}, 400
            

            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            return restaurant_pizza.to_dict(), 201
        except Exception as e:
         return {'errors': ['validation errors']}, 400



class RestaurantById(Resource):
    def get(self, id):

        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        return restaurant.to_dict(), 200
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
    
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizzas_data = []
        for pizza in pizzas:
            pizzas_data.append({
                'id': pizza.id,
                'name': pizza.name,
                'ingredients': pizza.ingredients
            })
        return pizzas_data, 200





api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')
api.add_resource(Pizzas, '/pizzas')




if __name__ == "__main__":
    app.run(port=5555, debug=True)
