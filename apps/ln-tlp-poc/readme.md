# **POC of Time-Lock Puzzle (TLP) on the Lightning Network (LN)**  

This project demonstrates a Proof of Concept (POC) for implementing a **Time-Lock Puzzle (TLP)** mechanism using the Lightning Network (LN). The following guide will walk you through setting up the required dependencies, running the app, and using Docker as an alternative method for deployment.

---

## **Prerequisites**

Make sure your system has the following dependencies installed:

### 1. **Install Go (v1.23.2 or greater)**  
- Follow the [official Go installation guide](https://go.dev/doc/install) to install Go.

After installation, ensure Go is correctly installed by running:

```bash
go version
```

### 2. **Install Python (v3.8 or greater)**  
- Visit the [official Python download page](https://www.python.org/downloads/) to install the required version.  
- Verify Python installation with:

```bash
python3 --version
```

**Tip:** You might also want to install `pip`, the Python package manager, if it is not already installed.

### 3. **Install LND (Lightning Network Daemon)**  
LND is required to interact with the Lightning Network. Follow these steps to install LND:

```bash
mkdir -p $GOPATH/src/github.com/lightningnetwork && \
git clone https://github.com/lightningnetwork/lnd.git $GOPATH/src/github.com/lightningnetwork/lnd && \
cd $GOPATH/src/github.com/lightningnetwork/lnd && \
make && make install
```

After installation, confirm LND is installed by running:

```bash
lnd --version
```

### 4. **Install BTCD (Bitcoin Daemon)**  
BTCD is a Bitcoin implementation in Go, used to manage the blockchain network. Install it using:

```bash
git clone https://github.com/btcsuite/btcd $GOPATH/src/github.com/btcsuite/btcd && \
cd $GOPATH/src/github.com/btcsuite/btcd && \
go install . ./cmd/...
```

Check the BTCD installation:

```bash
btcd --version
```

---

## **Starting the App**

### 1. **Navigate to the App Directory**

Make sure you are in the project’s root directory where the `start.sh` script is located:

```bash
cd /path/to/app
```

### 2. **Run the Application**

Execute the `start.sh` script to set up and run the application:

```bash
./start.sh
```

This script will:
- Initialize the LND and BTCD daemons.
- Set up the Lightning Network channels.
- Run the Python-based logic for the **Time-Lock Puzzle (TLP)** on the Lightning Network.

---

## **Using Docker (Optional)**

If you prefer to use Docker, follow these steps to build and run the application in a container.

### 1. **Build the Docker Image**

```bash
docker build -t tlp-ln-image .
```

### 2. **Create and Run the Docker Container**

```bash
docker run --name tlp-ln-container -p 9735:9735 -p 10009:10009 tlp-ln-image
```

> **Note:** Ensure that the required ports (9735 for LND and 10009 for RPC communication) are exposed and not blocked by firewalls.  
> **Additional Steps:** Some additional setup may be required, such as creating wallet credentials or initializing channels. Refer to the logs for instructions or errors during container setup.

---

## **Additional Setup (Optional)**

1. **Environment Variables:**
   - You can configure your wallet password, node IP, and other sensitive information using environment variables.
   - Example:
     ```bash
     export WALLET_PASS="your_wallet_password"
     export LND_NODE_IP="127.0.0.1"
     export LND_NETWORK="simnet"
     ```

2. **Create a Wallet (LND):**

```bash
lncli --rpcserver=127.0.0.1:10009 create
```

3. **Unlock the Wallet (LND):**

```bash
lncli --rpcserver=127.0.0.1:10009 unlock
```

---

## **Testing the Setup**

After running the app, you can verify that:
- **LND** and **BTCD** are running without errors.
- The **Lightning Network nodes** are connected and operational.
- You are able to create channels and perform transactions using the TLP logic.

---

## **Troubleshooting Tips**

- If any process is using the required ports (e.g., 10009 or 9735), kill those processes before starting LND:
  ```bash
  lsof -i :10009 | grep LISTEN
  kill -9 <PID>
  ```

- Ensure that all dependencies are correctly installed and environment variables are set.

---

## **Contributing**
TODO

---

## **License**

TODO