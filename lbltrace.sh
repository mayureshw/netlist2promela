#!/bin/sh

# Convert strings of state[n] form to their #defined state name in promela file
# to make trace more readable

PML=$1
TRACE=$2

if [ ! -f "$PML" ]
then
    echo PML file not found/specified: $PML
    exit 1
fi

if [ ! -f "$TRACE" ]
then
    echo TRACE file not found/specified: $TRACE
    exit 1
fi

awk '
/^#define i_/ {
    printf "s/\\<state\\[%s\\]/%s/g\n", $3, $2
    next
    }
' $PML | sed -f - -i $TRACE
