#!/bin/bash
# one line of jobs.txt: name|ENV...
cd "$(dirname "$0")"; name="${1%%|*}"; envs="${1#*|}"
eval "export $envs"; export TR_WATCH="44be"
bash run.sh "$name" >/dev/null 2>&1; rm -rf "out/$name/mame"
