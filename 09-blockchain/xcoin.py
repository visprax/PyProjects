#!/usr/bin/env python3

"""A simple blockchain application."""

import uuid
import flask
import logging
import argparse

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
    proof = blockchain.proof_of_work(last_block)
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
    required_fields = ["sender", "recipient", "amount"]
    if not all(field in values for field in required_fields):
        logger.error(f"didn't receive all the required fields, got: {values}")
        return "Missing values", 400
    logger.info(f"adding new transaction: {values}")
    # create the new transaction
    index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
    response = {"message": f"Transaction will be added to block with index: {index}"}
    return  flask.jsonify(response), 201

@app.route("/chain", methods=["GET"])
def full_chain():
    logger.info("getting the entire chain.")
    response = {
            "chain": blockchain.chain,
            "length": len(blockchain.chain)
            }
    return flask.jsonify(response), 200

@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = flask.request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return "Error: no nodes provided.", 400

    logger.info(f"registering new nodes on the network: {nodes}")
    for node in nodes:
        blockchain.register_node(node)
    response = {
            "message": "Added new nodes to the blockchain network.",
            "nodes": list(blockchain.nodes)
            }
    return flask.jsonify(response), 201

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    logger.info("applying consensus algorithm to resolve conflicts among nodes.")
    replaced = blockchain.resolve_conflict()
    if replaced:
        response = {
                "message": "The chain was replaced.",
                "new_chain": blockchain.chain
                }
    else:
        response = {
                "message": "The current chain is authorative.",
                "chain": blockchain.chain
                }
    return flask.jsonify(response), 200


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(prog="xcoin", description="a rudimentary blockchain implementation")
    parser.add_argument("-p", "--port", default=5000, type=int, help="the port to listen on")
    args = parser.parse_args()
    port = args.port
    
    logger.info(f"starting the node: {node_id}")
    app.run(host="0.0.0.0", port=port)
