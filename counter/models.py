from application import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    wallet_address = db.Column(db.String(200), unique=True, nullable=False)
    contract = db.Column(db.String(200), nullable=True)

    password = db.Column(db.String(120))
    is_verified = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(
        self,
        first_name,
        last_name,
        email,
        wallet_address,
        contract,
        password,
        is_verified,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.wallet_address = wallet_address
        self.contract = contract
        self.password = password
        self.is_verified = is_verified

    def __repr__(self):
        return "<Email %r>" % self.email
