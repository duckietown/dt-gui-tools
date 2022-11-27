#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# YOUR CODE BELOW THIS LINE
# ----------------------------------------------------------------------------


# NOTE: Use the variable DT_REPO_PATH to know the absolute path to your code
# NOTE: Use `dt-exec COMMAND` to run the main process (blocking process)

# constants
JUPYTER_WS="/jupyter_ws"
JUPYTER_PWD=quackquack
JUPYTER_TOKEN=$(python3 -c "from notebook.auth import passwd; print(passwd('${JUPYTER_PWD}'))")
JUPYTER_CMD="jupyter lab --NotebookApp.password='${JUPYTER_TOKEN}' --NotebookApp.allow_password_change=False"

# configure environment
set +e

# read arguments
args=""
for arg in "$@"; do
    args="${args} --${arg}"
done
JUPYTER_CMD="${JUPYTER_CMD} ${args}"

# create directory if it does not exist
if [ ! -d "${JUPYTER_WS}" ]; then
    mkdir -p "${JUPYTER_WS}"
fi
cd "${JUPYTER_WS}" || exit

# check HOME
if [ "${UID}" -ne "0" ] && [ "${HOME}" = "/" ]; then
    # we are not root but the HOME was not set, redirect HOME to /tmp
    HOME=/tmp
    export HOME
fi

# check volume
mountpoint -q "${JUPYTER_WS}"
if [ $? -ne 0 ]; then
    echo "WARNING: The path '${JUPYTER_WS}' is not a VOLUME. All the changes will be deleted with the container."
fi

# Start Xvfbs
echo "$prefix Starting xvfb"
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
xvfb=$!
echo "$prefix Started xvfb with PID $xvfb" 1>&2
export DISPLAY=:99
sleep 2

# run jupyter
dt-exec ${JUPYTER_CMD}


# ----------------------------------------------------------------------------
# YOUR CODE ABOVE THIS LINE

# wait for app to end
dt-launchfile-join
kill $xvfb