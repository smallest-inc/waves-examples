#!/bin/bash
set -e

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "You are not in a virtual environment."
    exit 1
fi

pip install -e ./livekit-plugins-smallestai --config-settings editable_mode=strict # change the path accordingly