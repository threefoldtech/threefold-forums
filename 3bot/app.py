from uuid import uuid3
import base64
import json

from nacl.public import Box
import nacl.encoding
import nacl.signing
import requests

from flask import Flask, session, redirect, url_for, request, abort, jsonify
from flask_sessionstore import Session
import os

app = Flask(__name__)
app.config['private_key'] = os.environ['THREEBOT_PRIVATE_KEY']
SECRET_KEY = os.environ['FLASK_SECRET_KEY']
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
  return jsonify(
    {'state': state, 'pk': public_key.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()})


@app.route('/data')
def data():
  data = request.args.get('signedAttempt')

  if not data:
    return abort(400, jsonify({'message': 'Bad request, some params are missing'}))

  data = json.loads(data)

  username = data['doubleName']
  if not username:
    return abort(400, jsonify({'message': 'Bad request, some params are missing'}))

  res = requests.get(os.environ['THREEBOT_URL'] + '/api/users/{0}'.format(username),
                     {'Content-Type': 'application/json'})
  if res.status_code != 200:
    return abort(400, jsonify({'message': 'Error getting user pub key'}))

  user_pub_key = nacl.signing.VerifyKey(res.json()['publicKey'], encoder=nacl.encoding.Base64Encoder)

  # verify data
  signedData = data['signedAttempt']
  if not signedData:
    return abort(400, jsonify({'message': 'Bad request, some params are missing'}))

  verifiedData = user_pub_key.verify(base64.b64decode(signedData)).decode()

  data = json.loads(verifiedData)

  if not data:
    return abort(400, jsonify({'message': 'Bad request, some params are missing'}))

  if data['doubleName'] != username:
    return abort(400, jsonify({'message': 'Bad request'}))

  # verify state
  state = data['signedState']

  if not state:
    return abort(400, jsonify({'message': 'Bad request'}))

  nonce = base64.b64decode(data['data']['nonce'])

  ciphertext = base64.b64decode(data['data']['ciphertext'])

  private_key = nacl.signing.SigningKey(app.config['private_key'], encoder=nacl.encoding.Base64Encoder)

  box = Box(
    private_key.to_curve25519_private_key(),
    user_pub_key.to_curve25519_public_key()
  )

  try:
    decrypted = box.decrypt(ciphertext, nonce)
    result = json.loads(decrypted)
    email = result['email']['email']
    sei = result['email']['sei']
    res = requests.post(os.environ['OPEN_KYC_URL'], headers={'Content-Type': 'application/json'},
                        json={'signedEmailIdentifier': sei})
    if res.status_code != 200:
      return abort(400, jsonify({'message': 'Email not verified!'}))
    result['email']['username'] = username
    return jsonify(result['email'])
  except:
    return abort(400, jsonify({'message': 'Error decrypting'}))


if __name__ == "__main__":
  app.run()
