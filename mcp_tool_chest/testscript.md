# WOLFRAM API:

### A sample API call (tested and works):
```html
https://www.wolframalpha.com/api/v1/llm-api?input=10+densest+elemental+metals&appid=WOLFRAM_API_KEY
```
### A simple test call to the mcp stdio server (tested and works):
```shell
(
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
  echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"wolfram_query","arguments":{"query":"solve x^2 = 4"}}}'
) | python -u wolfram_tools.py
```