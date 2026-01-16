import json
import os
import time
from web3 import Web3
from dotenv import load_dotenv

# 1. Load env
load_dotenv()

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# 2. Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Web3 not connected"

account = w3.eth.account.from_key(PRIVATE_KEY)

# 3. Load ABI
with open("abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

# -------------------------
# GET function (read-only)
# -------------------------
def get_string():
    value = contract.functions.getString().call()
    print("Current value on chain:")
    print(value)

# -------------------------
# SET function (write tx)
# -------------------------


def set_string(new_value: str):
    print("About to setString =", repr(new_value))

    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.functions.setString(new_value).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": 11155111,   # Sepolia
        "gas": 120000,
        "maxFeePerGas": w3.to_wei("30", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("1.5", "gwei"),
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print("Transaction sent:", tx_hash.hex())

    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Status:", receipt.status)
    print("Confirmed in block:", receipt.blockNumber)

    if receipt.status != 1:
        print(" Transaction failed / reverted")
        return

    
    value_at_confirmed = contract.functions.getString().call(
        block_identifier=receipt.blockNumber
    )
    print("Value read at confirmed block:")
    print(value_at_confirmed)

    # wait longer）
    for i in range(5):
        time.sleep(2)
        latest_value = contract.functions.getString().call()
        #print(f"Latest read try {i+1}: {latest_value}")
        if latest_value == new_value:
            print("Latest state synced")
            break




import requests

def fetch_random_string() -> str:
    """
    Fetch a random fact from an external API.
    Each call returns a different string.
    """
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["text"]

# -------------------------
# Run here (manual switch)
# -------------------------
if __name__ == "__main__":
    #get_string()
    set_string(fetch_random_string())
    #print(fetch_random_string())