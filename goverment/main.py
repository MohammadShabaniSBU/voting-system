from flask import Flask, jsonify, request
from phe import paillier
from blockchain import BlockChain
import requests

app = Flask(__name__)

public_key: paillier.PaillierPublicKey = None
private_key: paillier.PaillierPrivateKey = None

locals = []

def init():
    pub_key, priv_key = paillier.generate_paillier_keypair()

    global public_key, private_key
    public_key = pub_key
    private_key = priv_key

@app.route('/introduce', methods=['POST'])
def introduce():
    if request.json['url'] not in locals:
        locals.append(request.json['url'])

    response = {
        'public_key': {
            'n': public_key.n,
            'g': public_key.g,
        }
    }

    return jsonify(response)


@app.route('/collect-votes')
def collect_votes():
    counter = 0
    enc_vote_count = public_key.encrypt(0)

    for url in locals:
        res = requests.get(f'{url}/end_voting')
        data = res.json()

        counter += int(data['user_count'])
        enc_vote_count = enc_vote_count + paillier.EncryptedNumber(public_key, int(data['vote_count']))

    return jsonify({
        'vote_count': private_key.decrypt(enc_vote_count),
        'user_count': counter,
    })

if __name__ == '__main__':
    init()
    app.run(debug=True, port=80, host='0.0.0.0')
