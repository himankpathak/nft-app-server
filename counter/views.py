from flask import Blueprint, make_response
from flask import jsonify, request
from flask_cors import cross_origin
from application import db
from counter.models import Users
from pprint import pprint
import json

from werkzeug.security import generate_password_hash, check_password_hash

import openai
from settings import OPENAI_KEY

counter_app = Blueprint("counter_app", __name__)

openai.api_key = OPENAI_KEY


@counter_app.route("/")
@cross_origin(supports_credentials=True)
def init():
    return "This is the Twilio App working"


@counter_app.route("/signup", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def signup():
    if request.method == "POST":
        data = json.loads(request.data)
        firstName = data["firstName"]
        lastName = data["lastName"]
        email = data["email"]
        wallet_address = data["wallet_address"]
        print(wallet_address)
        password = data["password"]

        user = Users(
            first_name=firstName,
            last_name=lastName,
            email=email,
            wallet_address=wallet_address,
            password=generate_password_hash(password),
            is_verified=True,
        )
        db.session.add(user)
        db.session.commit()

        return {}, 200

    return {}, 400


@counter_app.route("/login", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def signin():
    if request.method == "POST":
        data = json.loads(request.data)
        email = data["email"]
        password = data["password"]
        user = Users.query.filter_by(email=data["email"]).first()
        if user and check_password_hash(user.password, password):
            return {}, 200
        return {}, 400


@counter_app.route("/chat", methods=["GET", "POST"])
def chat():
    data = json.loads(request.data)

    messages = data["messages"]

    chatbot = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    messages.append(chatbot.choices[0].message)
    return jsonify(messages), 200
