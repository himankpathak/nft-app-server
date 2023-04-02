# NFT Bloom Backend

NFT Bloom is an AI chatbot that helps people deal with mental health issues while gamifying the progress made by the user by rewarding them with Non-fungible tokens.

> You will need to setup both frontend and backend to run NFT Bloom.<br>
> NFT Bloom Frontend is located at https://github.com/himankpathak/nft-app-fe

### Instructions
- Make sure you have `docker` and `docker-compose` installed on your machine.
- Create a empty .flaskenv file for environment secrets.
```
FLASK_APP=manage.py
FLASK_ENV=development
SECRET_KEY=my_secret_key
DB_USERNAME=app_user
DB_PASSWORD=app_password
DB_HOST=127.0.0.1
DATABASE_NAME=app
OPENAI_KEY=<INSERT_YOUR_OPENAI_API_KEY_HERE>
WIRE_API_KEY=<INSERT_YOUR_VERBWIRE_API_KEY_HERE>
```
- Run `docker-compose up --build` to build the image and start the containers.
- To migrate the database tables first time you will need to run `docker-compose run --rm api poetry run flask db upgrade`.
- Run `docker-compose up -d` to start containers if not already up and running.
