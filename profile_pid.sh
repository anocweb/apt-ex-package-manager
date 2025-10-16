#!/bin/bash

TIMEOUT=10
PID=""

for arg in "$@"; do
    case $arg in
        --timeout=*)
            TIMEOUT="${arg#*=}"
            ;;
        *)
            PID="$arg"
            ;;
    esac
done

if [ -z "$PID" ]; then
    echo "Usage: $0 [--timeout=SECONDS] PID"
    exit 1
fi

austin -p $PID -o category_click_lockup.austin &
AUSTIN_PID=$!

echo "Profiling PID $PID for $TIMEOUT seconds..."
sleep $TIMEOUT
kill $AUSTIN_PID
echo "Profile saved to category_click_lockup.austin"