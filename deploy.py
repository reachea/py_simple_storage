from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# installing solcx compiler
print("Installing compiler")
install_solc(version="0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)


# write compiled sol to json
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# basic requirement for connection
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

chain_id = 1337
my_address = "0x7720B391867b285281E418786BAB3355Bcc27163"
private_key = os.getenv("PRIVATE_KEY")

# creating contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get nonce
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("deployed on:" + tx_receipt.contractAddress)

# call function
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

print(simple_storage.functions.retrieve().call())

# changing contract state

# 1. build transaction
store_tx = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

# 2. sign transaction
signed_store_tx = w3.eth.account.signTransaction(store_tx, private_key=private_key)

# 3. send transaction
store_tx_hash = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)

store_tx_receipt = w3.eth.wait_for_transaction_receipt(store_tx_hash)

# checking value

print(simple_storage.functions.retrieve().call())
