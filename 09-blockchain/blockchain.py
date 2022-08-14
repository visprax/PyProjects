#!/usr/bin/env python3

"""A rudimentary blockchain implementation."""

import os
import time
import json
import logging
import hashlib

logger = logging.getLogger("blockchain")

class Blockchain:
    """A rudimentary blockchain implementation.
    
    TODO: a simple explanation of a blockchain.

    """
    def __init__(self):
        logger.info("starting the blockchain.")
        self.chain = []
        self.transactions = []
        
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
            "previous_hash": previous_hash if previous_hash else self.hash(self.chain[-1])
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
        logger.info(f"adding the transaction from {sender} to {recipient}, amount: {}")
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
    def hash(block):
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



