import asyncio
from pathlib import Path
import os
from hashlib import sha256
import secrets
import gmpy2
from lndgrpc import LNDClient
from lndgrpc import AsyncLNDClient
import time
import json

from tlp import PrimeGenerator


# Fetching environment variables
network = os.getenv("LND_NETWORK", "simnet")
# Fetching credential path from environment or using default path
credential_path_env = os.getenv("LND_CRED_PATH", "alice/data/")
credential_path = Path(credential_path_env).expanduser().absolute()
data_path = f"chain/bitcoin/{network}"
# Macaroon and TLS paths
mac = credential_path.joinpath(f"{data_path}/admin.macaroon").absolute()
# tls = credential_path.joinpath(f"{data_path}/tls.cert").absolute()
# for linux use
tls = Path.home().joinpath(".lnd/tls.cert").absolute()
# Make sure paths are strings
mac_path = str(mac)
tls_path = str(tls)

# Node IP and port
node_ip = os.getenv("LND_NODE_IP", "localhost")
node_port = os.getenv("LND_NODE_PORT", 10005)
lnd_ip_port = f"{node_ip}:{node_port}"

# Example usage of LNDClient with TLS enabled
lnd = LNDClient(lnd_ip_port, macaroon_filepath=mac, cert_filepath=tls, no_tls=False)
lnd_async = AsyncLNDClient(
    lnd_ip_port, macaroon_filepath=mac, cert_filepath=tls, no_tls=False
)


#
def connect_peer(destination, host, retries=5):
    """Retry peer connection if it fails initially."""
    for attempt in range(retries):
        try:
            print(f"Attempting to connect to peer (Attempt {attempt + 1}/{retries})...")
            lnd.connect_peer(pub_key=destination, host=host)
            print("Connected to peer successfully.")
            return
        except Exception as e:
            print(f"Connection failed: {e}")
            time.sleep(2)  # Wait and retry

    raise Exception("Unable to connect to peer after multiple attempts.")


#
def unlock_wallet():
    """Unlock the existing wallet if it is locked."""
    print("Unlocking the wallet...")
    try:
        unlock_response = lnd.unlock_wallet(wallet_password=wallet_password)
        print("Wallet unlocked successfully:", unlock_response)
    except Exception as unlock_error:
        error_message = str(unlock_error).lower()
        print(f"Error unlocking wallet: {error_message}")

        # Check if the wallet is already unlocked
        if "wallet already unlocked" in error_message:
            print("Wallet is already unlocked.")
        else:
            raise  # Re-raise any other unexpected errors


mnemonic = [
    "immune",
    "rhythm",
    "bronze",
    "actor",
    "sail",
    "often",
    "pencil",
    "once",
    "palm",
    "skirt",
    "shiver",
    "drill",
    "exact",
    "moral",
    "draft",
    "venture",
    "plastic",
    "vault",
    "mango",
    "weasel",
    "onion",
    "bamboo",
    "dice",
    "scout",
]

wallet_password = "12345678".encode()

# Setup
keySendPreimageType = 5482373484
messageType = 34349334
preimageByteLength = 32
preimage = secrets.token_bytes(preimageByteLength)
m = sha256()
m.update(preimage)
preimage_hash = m.digest()


#
def get_tlp_computation():
    prime_gen = PrimeGenerator(bits=256)
    prime1 = prime_gen.generate_prime()
    prime2 = prime_gen.generate_prime()
    product = prime1 * prime2
    t = gmpy2.mpz(1000)
    baseg = prime_gen.generate_base()
    carmichael_p = prime_gen.calculate_carmichael(prime1, prime2)
    base2 = gmpy2.mpz(2)

    fast_exponent = prime_gen.mod_exp(base2, t, carmichael_p)
    fast_power = prime_gen.mod_exp(baseg, fast_exponent, product)

    return int(product), int(t), int(baseg), int(carmichael_p), int(fast_power)


def process_tlp(baseg, t, product):
    prime_gen = PrimeGenerator(bits=256)
    baseg = gmpy2.mpz(baseg)
    product = gmpy2.mpz(product)
    t = gmpy2.mpz(t)
    slow_power = baseg
    for _ in range(int(t)):
        slow_power = prime_gen.mod_exp(slow_power, gmpy2.mpz(2), product)

    return slow_power


amount_msat = 150

product, t, baseg, carmichael, fast_power = get_tlp_computation()

print("carmichael: ", carmichael)
print("fast_exponent: ", fast_power)


# lnd
addr = lnd.new_address(address_type=2)
print("Address: ", addr)
bal = lnd.wallet_balance()
bal_channel = lnd.channel_balance()
print("Wallet balance: ", bal)
print("Channel balance: ", bal_channel)
# Get node info
node_info = lnd.get_info()
print("Node Id ", node_info.identity_pubkey)

server_node_id = "0277c05921682a40b4b6d62d43ee4a2bf7196a1ead6788d95d13201ceffd942a27"
server_host = "localhost:10011"

connect_peer(server_node_id, server_host)
time.sleep(2)
lnd.open_channel(node_pubkey=server_node_id,local_funding_amount=50000,sat_per_byte=20)

# lnd.send_payment(payment_request="lnsb100u1pnse9d2pp5dxd60res6ke6t92degmp97uhrd5kqtwe5p2ssh7ztuvhtjx3qn6qdq5w3jhxapqd9h8vmmfvdjscqzzsxqyz5vqsp53dgv255hexjhyulh4d62ydcdazp692hmd25y2wkfxw23940s6f2s9qyyssqkjms549r6pn37h0c64vacapnnmsmfta4al3pqwj6fxddd048m6f5x6ssn9vvhdtgpvwrya9f34ckw2yruka3dphcsxsgvy874je68fcq4hrt79",fee_limit_msat=100000)

# send using sendpayment

message_payload = {
    "baseg": baseg,
    "product": product,
    "t": t,
    "destination": node_info.identity_pubkey,
}

message_json = json.dumps(message_payload).encode("utf-8")

custom_records = {34349334: message_json}


dest_custom_records = {
    keySendPreimageType: preimage,
    messageType: message_json,
}
random_bytes = secrets.token_bytes(32)


result = lnd.send_payment_v2(
    dest=bytes.fromhex(server_node_id),
    amt=amount_msat,
    payment_hash=preimage_hash,
    dest_custom_records=dest_custom_records,
    timeout_seconds=16,
    dest_features=[9],
    fee_limit_msat=100000,
    max_parts=1,
    final_cltv_delta=144,
    cltv_limit=148,
    amp=False,
    # route_hints=[routehint]
)


print("Send payment result: ", result)


async def subscribe_invoices():
    print("Listening for response from Server (BOB) ...")
    async for invoice in lnd_async.subscribe_invoices():
        # Extracting and decoding the custom message from custom_records
        message = None
        for htlc in invoice.htlcs:
            for key, value in htlc.custom_records.items():
                if key == 34349334:  # Standard keysend message key
                    try:
                        # Decode the byte-encoded value to a string
                        message_json_str = value.decode("utf-8")
                        # Parse the string into a JSON object (dictionary)
                        message = json.loads(message_json_str)
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        print(f"Error decoding JSON message: {e}")
                        message = {}

        # Print or save the extracted data
        if message != None:
            # check if amount sent is ok to proceed
            result = message["result"]

            print(f"SLOW result: {result} FAST result: {fast_power}")
            if int(result) == int(fast_power):
                print("TLP computation successful")
            else:
                print("TLP computation failed")
            exit()


async def run():
    coros = [subscribe_invoices()]
    await asyncio.gather(*coros)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
