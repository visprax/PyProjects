#!/usr/bin/env python3

"""A simple blockchain application."""

import uuid
import flask
import logging

from utils.blockchain import Blockchain

logger = logging.getLogger("xcoin")

# this is our node server in our blockchain network
app = flask.Flask("xcoin")

# universally unique id for this node
node_id = uuid.uuid4().hex
logger.debug(f"universal unique id for the node: {node_id}")

blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)
    # reward the node for mining the new block
    blockchain.new_transaction(sender="0", recipient=node_id, amount=1)
    # forge the block by adding it to the chain
    previous_hash = blockchain.block_hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
            "message": "New block forged.",
            "index": block["index"],
            "transactions": block["transactions"],
            "proof": block["proof"],
            "previous_hash": block["previous_hash"]
            }
    return flask.jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = flask.request.get_json()
    required_fields = ["sender", "ricipient", "amount"]
    if not all(field in values for field in required_fields):
        logger.error(f"didn't receive all the required fields, got: {values}")
        return "Missing values", 400
    # create the new transaction
    index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
    response = {"message": f"Transaction will be added to block with index: {index}"}
    return  flask.jsonify(response), 201

@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
            "chain": blockchain.chain,
            "length": len(blockchain.chain)
            }
    return flask.jsonify(response), 200
