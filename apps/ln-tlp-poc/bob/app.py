import asyncio
from hashlib import sha256
import secrets
import gmpy2
from lndgrpc import AsyncLNDClient
from lndgrpc import LNDClient
from pathlib import Path
import os
import json
import time
from tlp import PrimeGenerator

# start the node server


# Fetching environment variables
network = os.getenv("LND_NETWORK", "simnet")
# Fetching credential path from environment or using default path
credential_path_env = os.getenv("LND_CRED_PATH", "bob/data/")
credential_path = Path(credential_path_env).expanduser().absolute()
data_path = f"chain/bitcoin/{network}"
# Macaroon and TLS paths
mac = credential_path.joinpath(f"{data_path}/admin.macaroon").absolute()
# tls = credential_path.joinpath(f"{data_path}/tls.cert").absolute()
tls = Path.home().joinpath(".lnd/tls.cert").absolute()
# Make sure paths are strings
mac_path = str(mac)
tls_path = str(tls)


# Node IP and port
node_ip = os.getenv("LND_NODE_IP", "localhost")
node_port = os.getenv("LND_NODE_PORT", 10002)
lnd_ip_port = f"{node_ip}:{node_port}"


lnd = LNDClient(
    lnd_ip_port, macaroon_filepath=mac_path, cert_filepath=tls, no_tls=False
)
lnd
async_lnd = AsyncLNDClient(
    lnd_ip_port, macaroon_filepath=mac_path, cert_filepath=tls, no_tls=False
)

wallet_address = lnd.new_address(address_type=1)

# maybe have a remote db to store each clients node info so we can connect to them
client_nodes = [{
    "pub_key": "0284571a57ef1bae67de745f88ec2e1938a0509b5f8512bb258ce68aea050b9165",
    "host": "localhost:10005",
},]


# loop peers and open channel (connect to all peers)
if len(client_nodes) == 0:
    print("No peers to connect to")
    # connect to peers in channels
    exit(0)
    for peer in client_nodes:
        lnd.connect_peer(pub_key=peer["pub_key"], host=peer["host"])
        time.sleep(5)
        lnd.open_channel(
        node_pubkey=peer["pub_key"], local_funding_amount=50000, sat_per_byte=20
    )


# Get node info
node_info = lnd.get_info()
print("Node Id ", node_info.identity_pubkey)

# print("peers ", peers)
# inv= lnd.add_invoice(value=10000, memo="test invoice")
# print("Invoice ", inv)
#


# Time-Lock Puzzle (TLP) processing
def process_tlp(baseg, t, product):
    prime_gen = PrimeGenerator(bits=256)
    baseg = gmpy2.mpz(baseg)
    product = gmpy2.mpz(product)
    t = gmpy2.mpz(t)
    slow_power = baseg
    for _ in range(int(t)):
        slow_power = prime_gen.mod_exp(slow_power, gmpy2.mpz(2), product)

    return slow_power


async def subscribe_invoices():
    print("Listening for invoices...")
    async for invoice in async_lnd.subscribe_invoices():
        amount_msat = invoice.value_msat if invoice.value_msat else 0
        if amount_msat < 100:
            raise ValueError("Insufficient amount to compute with")
        message = extract_message_from_invoice(invoice)
        if message is not None:
            send_response(
                t=message["t"],
                product=message["product"],
                baseg=message["baseg"],
                destination=message["destination"],
            )


def extract_message_from_invoice(invoice):
    message = None
    for htlc in invoice.htlcs:
        for key, value in htlc.custom_records.items():
            if key == 34349334:  # Standard keysend message key
                try:
                    message_json_str = value.decode("utf-8")
                    message = json.loads(message_json_str)
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    print(f"Error decoding JSON message: {e}")
                    message = {}
    return message


def send_response(t, product, baseg, destination):
    tlp_result = process_tlp(baseg, t, product)
    print("Result ", tlp_result)

    message_payload = {
        "result": f"{tlp_result}",
        "time_stamp": int(time.time()),
    }
    message_json = json.dumps(message_payload).encode("utf-8")

    # Setup
    keySendPreimageType = 5482373484
    messageType = 34349334
    preimageByteLength = 32
    preimage = secrets.token_bytes(preimageByteLength)
    m = sha256()
    m.update(preimage)
    preimage_hash = m.digest()

    amount_msat = 1  # we currently can't send 0 amount - so we send 1 sat (minimum)

    dest_custom_records = {
        keySendPreimageType: preimage,
        messageType: message_json,
    }

    lnd.send_payment_v2(
        # Node ID of the destination node,
        dest=bytes.fromhex(destination),
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


async def run():
    coros = [subscribe_invoices()]
    await asyncio.gather(*coros)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
