from phe import paillier
import requests
import os
import sys

def get_public_key():
    res = requests.get(f'{os.environ["LOCAL_URL"]}/key')
    return res.json()['n'], res.json()['g']


def main():
    n, g = get_public_key()

    # this package use only n parameter to create the public key
    # https://github.com/data61/python-paillier/blob/7d9911eb03c3c2d64399bc15405feb5e628379d1/phe/paillier.py#L86
    public_key = paillier.PaillierPublicKey(int(n))

    vote = sys.argv[1].strip()
    userId = sys.argv[2].strip()

    if vote != '1' and vote != '-1':
        print('Invalid vote. Please vote 1 or -1.')
        print('submited vote: ', vote)
        return

    enc_vote = public_key.encrypt(int(vote)).ciphertext()

    res = requests.post(f'{os.environ["LOCAL_URL"]}/vote', json={'vote': enc_vote, 'user_id': userId })

    print(res.json())

    print('Vote submitted!')


if __name__ == '__main__':
    main()
