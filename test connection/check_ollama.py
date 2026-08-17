import urllib.request

url = "http://127.0.0.1:11434/api/tags"

try:
    with urllib.request.urlopen(url, timeout=5) as response:
        print("Status:", response.status)
        print(response.read().decode())
except Exception as e:
    print("Ollama is not reachable:", e)