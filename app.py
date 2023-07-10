import json
from os import abort

from flask import Flask, request, jsonify, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import conf
from conf import API as api
from utils import AlchemyEncoder

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = conf.DB_CONNECT_URI  # URI для подключения к PostgreSQL
CORS(app)
db.init_app(app)


class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=True)
    power = db.Column(db.String, unique=False, nullable=True)
    alterego = db.Column(db.String, unique=False, nullable=True)


@app.route(api, methods=['PUT'])
def update_hero():
    if request.method == 'PUT':
        if request.json:
            _id = request.json.pop('id', None)
            if _id:

                data_to_update = request.json
                alterego = data_to_update.pop('alterEgo', '')
                data_to_update.update({'alterego': alterego})

                Hero.query.filter(Hero.id == _id).update(data_to_update)
                db.session.commit()

                return {'response': 'OK'}

                # TODO
                # Need alter table column from alterego to alterEgo for
                # Hero.query.filter(Hero.id == request.json.pop('id')).update(request.json)

            else:
                return 'Not Found', 404
        return 'Not Found', 404


@app.route(api, methods=['GET'])
def get_heroes():
    if request.args.get('name', None):
        term = f'%{request.args.get("name", "")}%'
        heroes = Hero.query.filter(Hero.name.like(term))
    else:
        heroes = Hero.query.all()

    return [{'id': it.id, 'name': it.name, 'alterEgo': it.alterego, 'power': it.power} for it in heroes]


@app.route(api + '/<int:id>', methods=['GET'])
def get_hero(id):
    hero = get_hero_obj(id)
    return {'id': hero.id, 'name': hero.name, 'power': hero.power, 'alterEgo': hero.alterego}


@app.route(api + '/<int:id>', methods=['DELETE'])
def delete_hero(id):
    hero = get_hero_obj(id)
    db.session.delete(hero)
    db.session.commit()
    return {'response': 'OK'}


@app.route(api + '/<string:name>', methods=['GET'])
def search_heroes(name):
    heroes = db.session.query(Hero).filter(Hero.name == name)
    return [{'id': it.id, 'name': it.name, 'alterEgo': it.alterego, 'power': it.power} for it in heroes]


def get_hero_obj(id): return Hero.query.get(id)


@app.route(api, methods=['POST'])
def add_hero():
    if request.method == 'POST':
        data = request.json
        data.pop('id', None)

        alterego = data.pop('alterEgo', '')
        data.update({'alterego': alterego})

        hero = Hero(**data)
        db.session.add(hero)
        db.session.commit()
        return {'id': hero.id, 'name': hero.name, 'power': hero.power, 'alterEgo': hero.alterego}
    else:
        return 'Bad Request', 403


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
