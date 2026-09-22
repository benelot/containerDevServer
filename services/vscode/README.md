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

## Option 2 — VS Code Desktop via Remote SSH

The code-server container is **not involved**. This path uses the host's SSH daemon.

1. Install the **Remote - SSH** extension in VS Code Desktop.
2. Open the Command Palette → **Remote-SSH: Connect to Host** → `user@HOST`.
3. VS Code installs its own server component on the host the first time you connect.

You get full performance (no browser overhead) and access to all local extensions.
The only requirement is that you can SSH into the host machine.

## Which to choose

| | Browser (code-server) | Desktop + Remote SSH |
|---|---|---|
| Local VS Code needed | No | Yes |
| Performance | Good | Best |
| Extensions | code-server marketplace | Full VS Code marketplace |
| Requires SSH access | No | Yes |
