#!/bin/bash

pkill -f inspector
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector python -u ./wolfram_tools.pys