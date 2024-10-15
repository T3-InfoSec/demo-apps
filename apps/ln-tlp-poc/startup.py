import os
import subprocess
import time


# Get environment variables with default fallback
network = os.getenv("LND_NETWORK", "simnet")
node_ip = os.getenv("LND_NODE_IP", "localhost")
node_port = os.getenv("LND_NODE_PORT", "10002")
lnd_cred_path = os.getenv("LND_CRED_PATH", os.path.expanduser("~/.lnd"))
btcd_cred_path = os.getenv("BTCD_CRED_PATH", os.path.expanduser("~/.btcd"))
rpcuser = os.getenv("RPC_USER", "admin")
rpcpass = os.getenv("RPC_PASS", "12345")
wallet_pass = os.getenv("WALLET_PASS", "12345678")

# Paths for configuration files
conf_path = os.path.join(lnd_cred_path, "lnd.conf")
btcd_conf_path = os.path.join(btcd_cred_path, "btcd.conf")

# Ensure the necessary directories exist
os.makedirs(lnd_cred_path, exist_ok=True)
os.makedirs(btcd_cred_path, exist_ok=True)

# Generate the lnd.conf content
lnd_conf_content = f"""
[Application Options]
datadir=data
logdir=log
debuglevel=info
accept-amp=true
accept-keysend=true

[Bitcoin]
bitcoin.{network}=1
bitcoin.active=1
bitcoin.node=btcd

[btcd]
btcd.rpcuser={rpcuser}
btcd.rpcpass={rpcpass}
"""

# Write the lnd.conf file
with open(conf_path, "w") as conf_file:
    conf_file.write(lnd_conf_content)
print(f"Generated lnd.conf at: {conf_path}")

# Start btcd
print("Starting btcd...")
btcd_command = [
    "btcd",
    f"--{network}",
    "--txindex",
    f"--rpcuser={rpcuser}",
    f"--rpcpass={rpcpass}",
    " --miningaddr=rpFSv9xfdFcYWZ7Z7ojpfXeRJdoCqJwznB",
]
btcd_process = subprocess.Popen(btcd_command)
time.sleep(5)  # Give btcd time to start
