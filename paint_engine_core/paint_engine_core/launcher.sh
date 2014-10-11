#!/bin/sh

"$@"
ECODE=$?
read X
echo
echo "Command exited with code $ECODE"
exit $ECODE
