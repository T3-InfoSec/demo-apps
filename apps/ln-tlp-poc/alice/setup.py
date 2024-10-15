import os
import subprocess
import time
import psutil
from lndgrpc import LNDClient
from pathlib import Path

# Environment variables with fallback values
network = os.getenv("LND_NETWORK", "simnet")
node_ip = os.getenv("LND_NODE_IP", "localhost")
node_port = int(os.getenv("LND_NODE_PORT", "10005"))
credential_path_env = os.getenv("LND_CRED_PATH", "alice/data/")
rpcuser = os.getenv("RPC_USER", "admin")
rpcpass = os.getenv("RPC_PASS", "12345")
wallet_pass = os.getenv("WALLET_PASS", "12345678")

mnemonic = [
    "absent",
    "deposit",
    "talk",
    "claim",
    "obvious",
    "divert",
    "enlist",
    "wrong",
    "caution",
    "jazz",
    "amazing",
    "spirit",
    "whip",
    "electric",
    "say",
    "universe",
    "deposit",
    "ankle",
    "quantum",
    "fitness",
    "burden",
    "twice",
    "achieve",
    "number",
]
wallet_password = wallet_pass.encode()

# Ports to ensure are free
ports_to_kill = [10005, 10013, 8003]


def kill_process_on_port(port):
    """Kill processes using the given port, limited to the current user."""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            connections = proc.connections(kind="inet")  # Get network connections
            for conn in connections:
                if conn.laddr.port == port:
                    print(
                        f"Killing process {proc.pid} ({proc.name()}) using port {port}..."
                    )
                    proc.terminate()
                    proc.wait(timeout=5)  # Gracefully wait for termination
                    print(f"Process {proc.pid} on port {port} terminated.")
                    return  # Stop after the first matching process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignore inaccessible or terminated processes


# Free all required ports before starting services
for port in ports_to_kill:
    kill_process_on_port(port)

# Start lnd
print("Starting lnd...")
lnd_command = [
    "lnd",
    f"--rpclisten={node_ip}:{node_port}",
    f"--listen={node_ip}:10013",
    f"--restlisten={node_ip}:8003",
    "--datadir=data",
    "--logdir=log",
    "--debuglevel=info",
    f"--bitcoin.{network}",
    "--bitcoin.active",
    "--bitcoin.node=btcd",
    f"--btcd.rpcuser={rpcuser}",
    f"--btcd.rpcpass={rpcpass}",
]

    # Prepare lncli command to create the wallet with user-provided password
lncli_command = [
        "lncli",
        f"--rpcserver={node_ip}:{node_port}",
        "--macaroonpath=alice/data/chain/bitcoin/simnet/admin.macaroon",
        "create"
    ]

    # Create the wallet, auto inputting the wallet password
with subprocess.Popen(lncli_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as lncli_process:
        stdout, stderr = lncli_process.communicate(input=wallet_pass + "\n")  # Provide wallet password as input

if lncli_process.returncode == 0:
        print("Wallet created successfully.")
else:
        print(f"Failed to create wallet: {stderr}")


try:
    time.sleep(5)  # Give lnd time to start    
    credential_path = Path(credential_path_env).expanduser().absolute()
    data_path = f"chain/bitcoin/{network}"
    # Unlock or create wallet
    lnd_ip_port = f"{node_ip}:{node_port}"
    mac = os.path.join(
        credential_path, f"{data_path}/admin.macaroon"
    )
    # tls = credential_path.joinpath(f"{data_path}/tls.cert").absolute()
    # for linux use
    tls = Path.home().joinpath(".lnd/tls.cert").absolute()

    mac_path = str(mac)
    tls_path = str(tls)
    lnd = LNDClient(
        lnd_ip_port, macaroon_filepath=mac_path, cert_filepath=tls_path, no_tls=False
    )

    try:
        lnd.init_wallet(
            mnemonic=mnemonic, password=wallet_password, recovery_window=10
        )
        lnd.unlock_wallet(wallet_password=wallet_pass.encode())
        print("Wallet unlocked successfully.")
    except Exception as e:
        print(f"Failed to unlock wallet: {e}")

    print("Setup complete. btcd and lnd are running.")
except Exception as e:
    print(f"Failed to start lnd: {e}")
time.sleep(2)  # Give lnd time to start