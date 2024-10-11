#!/bin/bash
set -e

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "You are not in a virtual environment."
    exit 1
fi

pip install -e /home/hamees/waves-examples/lightning/livekit_example/livekit-plugins-smallest --config-settings editable_mode=strict
