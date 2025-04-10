# /// script
# dependencies = [
#   "github-mcp-server-unofficial"
# ]
# ///

import subprocess

from github_mcp_server import find_github_mcp_server_bin

subprocess.run([find_github_mcp_server_bin()])
