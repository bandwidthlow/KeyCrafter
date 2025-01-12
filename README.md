# SSH Key Generator and Tunneling Tool

The SSH Key Generator and Tunneling Tool is a simple, GTK-based application for generating SSH keys and managing secure SSH tunnels. It’s designed to be user-friendly and efficient for developers and system administrators.



## ✨ Features

### 🔑 SSH Key Generation
- Generate SSH keys with the following types:
  - RSA
  - DSA
  - ECDSA
- Save keys in a custom directory.
- Configurable key length:
  - 2048
  - 3072
  - 4096
- Optional passphrase support for private keys.

### 👁️ SSH Key Viewer
- View private and public keys directly in the application.

### 🌐 SSH Tunneling
- Start and stop SSH tunnels seamlessly.
- Configure remote host, remote port, and local port.

## 📋 Prerequisites

Ensure the following are installed on your system:

- Python 3.6+
- GTK 3
- PyGObject
- Paramiko

## 🛠 Installation

1. Clone the repository:
```bash
   git clone https://github.com/bandwidthlow/KeyCrafter.git
   cd KeyCrafter
   ```

2. Install dependencies:
```bash
  pip install -r requirements.txt
```
3. Run the tool:
```bash
  python3 main.py
```

  


