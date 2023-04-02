from flask import Blueprint, make_response
from flask import jsonify, request
from flask_cors import cross_origin
from application import db
from counter.models import Users
from pprint import pprint
import json
import requests
import shutil
import random
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

            c = create_contract(wallet_address)

            user = Users(
                first_name=firstName,
                last_name=lastName,
                email=email,
                wallet_address=wallet_address,
                contract=c,
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
    email = data["email"]

    user = Users.query.filter_by(email=email).first()

    wallet_address = user.wallet_address
    contractAddress = user.contract

    images_words = ["batman", "fruit", "happy_ape", "superman"]
    if len(messages) >= 1:
        #image_search = random.choice(images_words) + ".png"
        positive_words = parse_positive_words()
        image_search = random.choice(positive_words)
        print('image_search', image_search)
        image_url = request_image(image_search)
        print('image url', image_url)
        save_image(image_url)
        mint_NFT_from_image(
            image_search,
            image_search + " picture",
            contractAddress,
            wallet_address,
            "new_image.png"
        )

    chatbot = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    messages.append(chatbot.choices[0].message)
    return jsonify(messages), 200


def mint_NFT_from_image(
    name_of_nft, description, contract_address, recepient_address, image_name
):
    url = "https://api.verbwire.com/v1/nft/mint/mintFromFile"
    files = {"filePath": (image_name, open(image_name, "rb"), "image/jpeg")}

    headers = {
        "accept": "application/json",
        "X-API-Key": WIRE_API_KEY,
    }

    body_params = {
        "name": name_of_nft,
        "description": description,
        "contractAddress": contract_address,
        "recipientAddress": recepient_address,
        "allowPlatformToOperateToken": "true",
        "data": "data",
        "quantity": 1,
        "chain": "goerli",
    }
    response = requests.post(
        url, headers=headers, data=body_params, files=files
    )
    print(response.json())


def request_image(search):
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

    querystring = {
        "q": search,
        "pageNumber": "1",
        "pageSize": "10",
        "autoCorrect": "true",
    }

    headers = {
        "X-RapidAPI-Key": "f1bc582251msh3c7fa67b028c964p1d56f5jsnceb5397f1478",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()["value"][random.randint(0, 9)]["url"]


def save_image(image_url):
    filename = "new_image.png"
    r = requests.get(image_url, stream=True)

    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        print("Image downloaded successfully")
    else:
        print("Image could not be downloaded")


def create_contract(wallet_address):
    url = "https://api.verbwire.com/v1/nft/deploy/deploySimpleContract"

    payload = f'-----011000010111000001101001\r\nContent-Disposition: form-data; name="chain"\r\n\r\ngoerli\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="contractType"\r\n\r\nnft721\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="contractName"\r\n\r\nrandom\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="contractSymbol"\r\n\r\nrandom\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="recipientAddress"\r\n\r\n{wallet_address}\r\n-----011000010111000001101001--\r\n\r\n'
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": WIRE_API_KEY,
    }

    response = requests.post(url, data=payload, headers=headers)
    print("response_contract address", response.text)
    return response.json()["transaction_details"]["createdContractAddress"]

def parse_positive_words(filename='positive_words.txt'):
    words = []
    with open(filename) as f:
        words.append(f.readline())
    return words
