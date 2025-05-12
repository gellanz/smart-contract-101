import os
from web3 import Web3
from solcx import compile_files
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
rpc_url = os.getenv("AVALANCHE_RPC_URL")
private_key = os.getenv("PRIVATE_KEY_BUYER")  # Deployer (e.g., buyer)
# Connect to Avalanche
w3 = Web3(Web3.HTTPProvider(rpc_url))
assert w3.is_connected(), "Failed to connect to Avalanche"

# Set deployer account
account = w3.eth.account.from_key(private_key)
w3.eth.default_account = account.address

# Compile Solidity contract
compiled = compile_files(
    ["contracts/PropertySale.sol"],
    import_remappings={"@openzeppelin": "./node_modules/@openzeppelin"}
)
contract_interface = compiled["contracts/PropertySale.sol:PropertySale"]

# Deploy contract
def deploy_contract():
    contract = w3.eth.contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface["bin"]
    )
    tx = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 3000000,
        "gasPrice": w3.to_wei("3", "gwei")
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contract deployed at: {receipt.contractAddress}")
    return receipt.contractAddress

# Save contract address and ABI for later use
contract_address = deploy_contract()
with open("contract.json", "w") as f:
    import json
    json.dump({"address": contract_address, "abi": contract_interface["abi"]}, f)