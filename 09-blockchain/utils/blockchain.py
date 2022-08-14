"""A rudimentary blockchain implementation."""

import time
import json
import logging
import hashlib
import requests
from urllib.parse import urlparse

logger = logging.getLogger("blockchain")

class Blockchain:
    """A rudimentary blockchain implementation.
    
    TODO: a simple explanation of a blockchain.
    """
    def __init__(self):
        logger.info("starting the blockchain.")
        self.chain = []
        self.transactions = []
        self.nodes = set()
        
        logger.info("creating the genesis block.")
        # create the genesis block
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """Create a new block in the blockchain.

        Args:
            proof (int): The proof given by the proof of work algorithm.
            previous_hash(int, optional): Hash of the previous block. Defaults to None.

        Returns:
            dict: The new block.
        """
        logger.info(f"adding the new block to the chain, timestamp: {time.time()}")
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.transactions,
            "proof": proof,
            "previous_hash": previous_hash if previous_hash else self.block_hash(self.chain[-1])
                }
        self.chain.append(block)
        logger.info("resetting the transactions list")
        # reset the transactions for the new block
        self.transactions = []
        return block
    
    def new_transaction(self, sender, recipient, amount):
        """Create a new transaction that will go into the next mined block.
        
        Args:
            sender (str): Address of the sender.
            recipient (str): Address of the recipient.
            amount (int): The amount of transaction.

        Returns:
            int: The index of the block that will hold this transaction.
        """
        logger.info(f"adding the transaction from {sender} to {recipient}, amount: {amount}")
        transaction = {
                "sender": sender,
                "recipient": recipient,
                "amount": amount
                }
        self.transactions.append(transaction)
        # return the index of block which the transaction will be added to
        return self.last_block["index"] + 1
    
    @property
    def last_block(self):
        """Get the last block in the chain."""
        return self.chain[-1]

    @staticmethod
    def block_hash(block):
        """Create the SHA256 hash of a block.

        Note:
            The block should be an ORDERED dictionary, Or the resulting hashes
                maybe inconsistent.

        Args:
            block (dict): The block to be hashed.

        Returns:
            str: The hash of the block.
        """
        logger.info("computing the hash of the block.")
        block_bytes = json.dumps(block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_bytes).hexdigest()
        return block_hash

    def proof_of_work(self, last_block):
        """A simple proof of work algorithm.

        Find a number, p, such that hash(p'p) begins with n consecutive zeros,
            where p' is the last block's proof.

        Args:
            last_proof (int): Proof of last block.

        Returns:
            proof (int): The current valid proof.
        """
        last_proof = last_block["proof"]
        last_hash = self.block_hash(last_block)
        proof = 0
        logger.info(f"computing proof of work...")
        isvalid = self.isvalid_proof(last_proof, last_hash, proof)
        while not isvalid:
            proof += 1
            isvalid = self.isvalid_proof(last_proof, last_hash, proof)
        logger.info(f"found a proof of work: {proof}")
        return proof
    
    @staticmethod
    def isvalid_proof(last_proof, last_hash, proof):
        """Validate a given proof in accordance with the difficulty.

        Validation is done such that hash(p'p), where p' is the last_proof 
            and p is the current proof begins with n consecutive zeros, n 
            is adjusted in accordance with the difficulty level.

        Args:
            last_proof (int): Proof of last block.
            proof (int): Proof of current block.

        Returns:
            bool: Wether the provided proof is a valid one.
        """
        difficulty = 4
        proof_statement = f"{last_proof}{proof}{last_hash}".encode()
        proof_statement_hash = hashlib.sha256(proof_statement).hexdigest()
        return proof_statement_hash[:difficulty] == '0'*difficulty
    
    def register_node(self, address):
        """Register a new node in the blockchain network.

        Args:
            address (str): The URL address of the node, e.g. "http://127.0.0.1:5000"

        Raises:
            ValueError: If the address is not valid URL.
        """
        parsed_url = urlparse(address) 
        hostname = parsed_url.hostname
        if not hostname:
            logger.error(f"can't get the hostname from node address: {address}")
            raise ValueError("Invalid node address.")
        port = parsed_url.port if parsed_url.port else "80"
        self.nodes.add(f"{hostname}:{port}")

    def resolve_conflict(self):
        """The consensus algorithm.

        If there is a longer chain in the network than ours, replace
            the current chain with that one.

        Returns:
            bool: True if the chained was replaces, False otherwise.
        """
        new_chain = None
        max_length = len(self.chain)
        logger.info("checking consensus among nodes.")
        for node in self.nodes:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                chain = reponse.json()["chain"]
                length = reponse.json()["length"]
                # if the node chain is a valid chain and is longer than 
                # current max_length, replace ours with that one
                if length > max_length and self.isvalid_chain(node, chain):
                    max_length = length
                    new_chain = chain
                    node_address = node
        if new_chain:
            logger.debug(f"replacing current chain with a new found longer, valid chain at: {node_address}")
            self.chain = new_chain
            return True
        return False

    def isvalid_chain(self, node, chain):
        """Check to see if a given chain is a valid blockchain.

        Args:
            chain (list(dict)): The chain of blocks.
            node (str): The address of node hosting the chain.
        
        Returns:
            bool: True if the chain is a valid blockchain, False otherwise.
        """
        last_block = chain[0]
        curr_idx = 1
        logger.info(f"checking validity of the chain of node: {node}")
        while curr_idx < len(chain):
            block = chain[curr_idx]
            # check the hash of the block
            last_block_hash = self.block_hash(last_block)
            if not block["previous_hash"] == last_block_hash:
                logger.warn("inconsistent hashed among blocks, the chain is not valid.")
                return False
            # check the proof of work
            if not self.isvalid_proof(last_block["proof"], last_block_hash, block["proof"]):
                logger.warn("inconsistent proof of work among blocks, the chain is not valid.")
                return False
            last_block = block
            curr_idx += 1
        return True

        

