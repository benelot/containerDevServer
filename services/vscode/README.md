# VS Code Service

Two independent ways to use VS Code on this server.

## Option 1 — Browser (code-server)

No local VS Code installation needed.

1. Start the service:
   ```bash
   ./scripts/start.sh vscode
   ```
2. Open `http://HOST:VSCODE_PORT` in your browser (default port 4000).
3. Enter the password from `VSCODE_PASSWORD` in `.env`.

The container mounts `VSCODE_WORKSPACE` (default `/home/coder/workspace`) as the
working directory. Set this to your actual project path before starting:

```bash
# In services/vscode/.env
VSCODE_WORKSPACE=/home/alice/projects
```

Extensions and settings are persisted in the `vscode_config` Docker volume across
container restarts.

---

## Option 2 — VS Code Desktop via Remote SSH

The code-server container is **not involved**. This uses the host's SSH daemon and
gives you full VS Code Desktop performance with all marketplace extensions.

### 1. Prerequisites

- VS Code Desktop installed on your local machine.
- SSH access to the server (ask the administrator for your account and hostname).

### 2. Set up SSH key authentication (recommended)

Password prompts every connection become annoying quickly. Run this once on your
**local machine**:

```bash
# Generate a key if you don't have one yet
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy the public key to the server
ssh-copy-id user@HOST
```

Test that it works without a password:
```bash
ssh user@HOST "echo ok"
```

### 3. Add the host to your SSH config (optional but convenient)

Edit `~/.ssh/config` on your local machine and add:

```
Host devserver
    HostName HOST
    User alice
    IdentityFile ~/.ssh/id_ed25519
```

After this you can type `ssh devserver` instead of `ssh alice@HOST` everywhere,
including in VS Code.

### 4. Install the Remote - SSH extension

In VS Code Desktop, open the Extensions panel and install:

- **Remote - SSH** (`ms-vscode-remote.remote-ssh`)

### 5. Connect

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
2. Run **Remote-SSH: Connect to Host**.
3. Enter `user@HOST` (or just `devserver` if you set up the SSH config above).
4. VS Code installs its own server component on the host the first time — this
   takes about a minute. Subsequent connects are instant.
5. Open the project folder: **File → Open Folder** → select the repo directory.

### 6. Port forwarding — access services at localhost

Once connected, VS Code can forward any port on the server to your local machine.
This means you can open `http://localhost:5000` in your local browser instead of
`http://HOST:5000`, which is useful on networks that block high port numbers.

**Forward a port:**
1. Open the **Ports** panel (bottom bar → "Ports", or `Ctrl+Shift+P` →
   "Forward a Port").
2. Click **Forward a Port**, enter the port number (e.g. `20000` for the
   auto-assigned MLflow port, or whatever `generate-ports.sh --show` printed).
3. VS Code adds it to the list and opens a `localhost:PORT` tunnel.

**Forward all service ports at once** (paste into your local terminal):
```bash
# Replace alice@devserver and port numbers with your values from generate-ports.sh --show
ssh -N \
  -L 5000:localhost:20000 \
  -L 9001:localhost:20003 \
  -L 8888:localhost:20008 \
  -L 3000:localhost:20010 \
  alice@devserver
```

Run `./scripts/generate-ports.sh --show` on the server to see your assigned ports.

### 7. Useful extensions to install on the remote

VS Code installs extensions on the **server side** when connected via Remote SSH.
Open the Extensions panel while connected and install:

- **Python** (`ms-python.python`) — language support, linting, debugging
- **Jupyter** (`ms-toolsai.jupyter`) — run `.ipynb` notebooks directly in VS Code
- **Docker** (`ms-azuretools.vscode-docker`) — manage containers from the sidebar
- **GitLens** (`eamodio.gitlens`) — enhanced Git history and blame

---

## Which to choose

| | Browser (code-server) | Desktop + Remote SSH |
|---|---|---|
| Local VS Code needed | No | Yes |
| Performance | Good | Best |
| Extensions | code-server marketplace | Full VS Code marketplace |
| Port forwarding | Not built-in | Built-in Ports panel |
| Requires SSH access | No | Yes |
| Setup effort | None | ~5 minutes |
