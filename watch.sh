#!/usr/bin/env bash
# Watches presentation.html and the images/ folder.
# Whenever they change, rebuilds presentation-single.html automatically.
cd "$(dirname "$0")"

last=""
while true; do
  sig=$(ls -l --time-style=+%s presentation.html images/* 2>/dev/null | md5sum)
  if [ "$sig" != "$last" ]; then
    last="$sig"
    ./build-single.sh
  fi
  sleep 3
done
