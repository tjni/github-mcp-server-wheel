# github-mcp-server-unofficial

Packages https://github.com/github/github-mcp-server as wheels.

## Usage

This package can be installed using:

```bash
pip install github-mcp-server-unofficial
```

If you are invoking it from a Python program, you can get a `Path` to this
binary using:

```python
import subprocess

from github_mcp_server import find_github_mcp_server_bin

subprocess.run([find_github_mcp_server_bin()])
```
