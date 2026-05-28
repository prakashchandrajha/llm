import json
import subprocess
import time

servers = {
    "context7": ["npx", "-y", "@upstash/context7-mcp"],
    "serena": ["serena", "start-mcp-server", "--project", "/home/vvd/prakash/xorz/llm"],
    "codebase-memory": ["npx", "-y", "codebase-memory-mcp"],
    "coderunner": ["npx", "-y", "@mcpc-tech/code-runner-mcp"]
}

for name, cmd in servers.items():
    print(f"--- Server: {name} ---")
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Initialize
        init_req = json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}})
        p.stdin.write(init_req + "\n")
        p.stdin.flush()
        
        # Read init response
        while True:
            line = p.stdout.readline()
            if not line: break
            try:
                data = json.loads(line)
                if "id" in data and data["id"] == 1:
                    break
            except:
                pass
                
        # Send initialized notification
        notif = json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})
        p.stdin.write(notif + "\n")
        p.stdin.flush()
        
        # Request tools
        tools_req = json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list"})
        p.stdin.write(tools_req + "\n")
        p.stdin.flush()
        
        tools = []
        while True:
            line = p.stdout.readline()
            if not line: break
            try:
                data = json.loads(line)
                if "id" in data and data["id"] == 2:
                    if "result" in data and "tools" in data["result"]:
                        tools = [t["name"] for t in data["result"]["tools"]]
                    break
            except:
                pass
                
        print(f"Tools: {tools}")
        p.terminate()
    except Exception as e:
        print(f"Error: {e}")
    print()
