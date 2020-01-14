from uuid import uuid4
import base64
import json

from nacl.public import Box
import nacl.encoding
import nacl.signing
import requests

from flask import Flask, session, redirect, url_for, request, abort, jsonify
from flask_sessionstore import Session

app = Flask(__name__)
app.config['private_key'] = '3x6Nbx8FQGTUG6sFT2hHpuxBAd1cTqQfkXvJJmNl/Z0='  # nacl.signing.SigningKey.generate().encode(nacl.encoding.Base64Encoder)
SECRET_KEY = "aefmwefklewklfnewkfnedwedwqefjewfqweofhqewoifhqewfoidqfqfqfwfqwm2e12ewfef23g23g3g23g32"
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
app.config.from_object(__name__)
Session(app)


@app.route('/pub_key')
def get_public_key():
    state = str(uuid4()).replace('-', '')
    session['state'] = state
    private_key = nacl.signing.SigningKey(app.config['private_key'], encoder=nacl.encoding.Base64Encoder)
    public_key = private_key.verify_key
    return jsonify ({'state': state, 'pk': public_key.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()})


@app.route('/data')
def data():
    signedhash = request.args.get('signedhash')
    username = request.args.get('username')
    data = request.args.get('data')

    if signedhash is None or username is None or data is None:
        return abort(400, jsonify({'message': 'Bad request, some params are missing'}))
    data = json.loads(data)

    res = requests.get('https://login.threefold.me/api/users/{0}'.format(username), {'Content-Type':'application/json'})
    if res.status_code != 200:
        return abort(400, jsonify({'message': 'Error getting user pub key'}))

    user_pub_key = nacl.signing.VerifyKey(res.json()['publicKey'], encoder=nacl.encoding.Base64Encoder)
    nonce = base64.b64decode(data['nonce'])
    ciphertext = base64.b64decode(data['ciphertext'])
    private_key = nacl.signing.SigningKey(app.config['private_key'], encoder=nacl.encoding.Base64Encoder)

    state = user_pub_key.verify(base64.b64decode(signedhash)).decode()
    # if state != session['state']:
    #     return abort(400, jsonify({'message': 'Invalid state. not matching one in user session'}))

    box = Box(
        private_key.to_curve25519_private_key(),
        user_pub_key.to_curve25519_public_key()
    )

    try:
        decrypted = box.decrypt(ciphertext, nonce)
        result = json.loads(decrypted)
        email = result['email']['email']
        emailVerified = result['email']['verified']
        if not emailVerified:
            return abort(400, jsonify({'message': 'Email not verified'}))
        return jsonify(result['email'])
    except:
        return abort(400, jsonify({'message': 'Error decrypting'}))


if __name__ == "__main__":


    app.run()
