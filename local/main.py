import json
from flask import Flask, jsonify, request, make_response
from blockchain import BlockChain
from phe import paillier
import requests
import os

app = Flask(__name__)
blockChain: BlockChain = None


def init():
    goverment_url = os.environ.get('GOVERMENT_URL')
    my_url = os.environ.get('MY_URL')

    res = requests.post(f'{goverment_url}/introduce', json={'url': my_url})

    global blockChain
    blockChain = BlockChain(json.dumps(res.json()['public_key']))


@app.route('/vote', methods=['POST'])
def vote():
    data = request.json

    if 'vote' in data and 'user_id' in data:
        blockChain.add_block(json.dumps(data))

        print('Vote stored')
        return jsonify({'message': 'Your vote has been recorded!'})

    return make_response(jsonify({'message': 'Invalid request!'}), 400)


@app.route('/key')
def key():
    public_key = json.loads(blockChain.get_head_data())

    return jsonify({
        'n': public_key['n'],
        'g': public_key['g'],
    })


@app.route('/end_voting')
def end_voting():
    head = blockChain.get_head()

    pub = json.loads(head.get_data())

    public_key = paillier.PaillierPublicKey(int(pub['n']))

    block = head.next_block
    counter = 0
    enc_vote_count = public_key.encrypt(0)

    while block != None:
        data = json.loads(block.get_data())

        enc_vote_count = enc_vote_count + paillier.EncryptedNumber(public_key, int(data['vote']))
        counter += 1
               
        block = block.next_block


    return jsonify({
        'vote_count': enc_vote_count.ciphertext(),
        'user_count': counter
    })


if __name__ == '__main__':
    init()
    app.run(debug=True, port=80, host='0.0.0.0')
