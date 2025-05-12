import os
from web3 import Web3
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
rpc_url = os.getenv("AVALANCHE_RPC_URL")
buyer_key = os.getenv("PRIVATE_KEY_BUYER")
seller_key = os.getenv("PRIVATE_KEY_SELLER")
notary_key = os.getenv("PRIVATE_KEY_NOTARY")
government_key = os.getenv("PRIVATE_KEY_GOVERNMENT")

# Connect to Avalanche
w3 = Web3(Web3.HTTPProvider(rpc_url))
assert w3.is_connected(), "Failed to connect to Avalanche"

# Load contract
with open("contract.json", "r") as f:
    contract_data = json.load(f)
contract_address = contract_data["address"]
contract_abi = contract_data["abi"]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Helper function to send transactions
def send_transaction(private_key, tx):
    account = w3.eth.account.from_key(private_key)
    tx["from"] = account.address
    tx["nonce"] = w3.eth.get_transaction_count(account.address)
    tx["gas"] = 200000
    tx["gasPrice"] = w3.to_wei("3", "gwei") 
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

# Stage 1: Buyer initiates sale
def initiate_sale(buyer_key, property_id, seller_address, notary_address, government_address, price_wei):
    tx = contract.functions.initiateSale(
        property_id,
        seller_address,
        notary_address,
        government_address,
        price_wei
    ).build_transaction({"value": price_wei})
    receipt = send_transaction(buyer_key, tx)
    print(f"Sale initiated for property {property_id}. Tx: {receipt.transactionHash.hex()}")

# Stage 2: Notary verifies
def verify_notary(notary_key, property_id):
    tx = contract.functions.verifyNotary(property_id).build_transaction()
    receipt = send_transaction(notary_key, tx)
    print(f"Notary verified for property {property_id}. Tx: {receipt.transactionHash.hex()}")

# Stage 3: Government verifies taxes
def verify_taxes(government_key, property_id, tax_amount_wei):
    tx = contract.functions.verifyTaxes(property_id, tax_amount_wei).build_transaction()
    receipt = send_transaction(government_key, tx)
    print(f"Taxes verified for property {property_id}. Tx: {receipt.transactionHash.hex()}")

# Stage 4: Buyer completes sale
def complete_sale(buyer_key, property_id):
    tx = contract.functions.completeSale(property_id).build_transaction()
    receipt = send_transaction(buyer_key, tx)
    print(f"Sale completed for property {property_id}. Tx: {receipt.transactionHash.hex()}")

# Example usage
if __name__ == "__main__":
    property_id = 1
    seller_address = w3.eth.account.from_key(seller_key).address
    notary_address = w3.eth.account.from_key(notary_key).address
    government_address = w3.eth.account.from_key(government_key).address
    price_wei = w3.to_wei("1", "ether")  # 1 AVAX
    tax_amount_wei = w3.to_wei("0.5", "ether")  # 0.5 AVAX tax

    # Execute stages
    initiate_sale(buyer_key, property_id, seller_address, notary_address, government_address, price_wei)
    #verify_notary(notary_key, property_id)
    #verify_taxes(government_key, property_id, tax_amount_wei)
    #complete_sale(buyer_key, property_id)