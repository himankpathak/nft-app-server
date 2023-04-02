from flask import Blueprint, make_response
from flask import jsonify, request
from flask_cors import cross_origin
from application import db
from counter.models import Users
from pprint import pprint
import json
import requests
from werkzeug.security import generate_password_hash, check_password_hash

import openai
from settings import OPENAI_KEY, WIRE_API_KEY

counter_app = Blueprint("counter_app", __name__)

openai.api_key = OPENAI_KEY


@counter_app.route("/")
@cross_origin(supports_credentials=True)
def init():
    return "This is the Twilio App working"


@counter_app.route("/signup", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def signup():
    try:
        if request.method == "POST":
            data = json.loads(request.data)
            firstName = data["firstName"]
            lastName = data["lastName"]
            email = data["email"]
            wallet_address = data["wallet_address"]
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
    except:
        pass
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


@counter_app.route("/nft/<email>", methods=["GET"])
def get_all_nfts_owned_by_wallet(email):
    try:
        user = Users.query.filter_by(email=email).first()
        wallet_address = user.wallet_address

        url = "https://api.verbwire.com/v1/nft/data/owned"

        headers = {"accept": "application/json", "X-API-Key": WIRE_API_KEY}

        query_params = {"walletAddress": wallet_address, "chain": "goerli"}

        response = requests.get(url, headers=headers, params=query_params)

        return (
            extract_image_token_uri(
                extract_image_metadata(
                    return_all_images_tokens(response.json())
                )
            ),
            200,
        )

    except Exception as e:
        pass
    return {}, 400


def return_all_images_tokens(all_wallet_images_json):
    tokens_list = []
    for x in all_wallet_images_json["nfts"]:
        tokens_list.append((x["contractAddress"], x["tokenID"], x["tokenName"]))

    return tokens_list


def extract_image_metadata(token_info):
    image_uris = []
    url = "https://api.verbwire.com/v1/nft/data/nftDetails"
    headers = {"accept": "application/json", "X-API-Key": WIRE_API_KEY}
    for x in token_info:
        query_params = {
            "contractAddress": x[0],
            "tokenId": x[1],
            "chain": "goerli",
        }
        response = requests.get(
            url, headers=headers, params=query_params
        ).json()
        image_uris.append(response["nft_details"]["tokenURI"])

    return image_uris


def clean_token_uri(token_uri):
    start_index = token_uri.index("//") + 2
    token_uri = "https://ipfs.io/ipfs/" + token_uri[start_index:]

    return token_uri


def extract_image_token_uri(image_metadata):
    token_uris = []
    for x in image_metadata:
        response = requests.get(x).json()
        token_uris.append(
            (response["name"], clean_token_uri(response["image"]))
        )

    return token_uris


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
