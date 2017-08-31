#!/usr/bin/env bash

echo "arg 1: $1"
echo "arg 2: $2"

MODE=$1
LOCAL=0
TESTING=0

if [ $# -eq 2 ]; then
    if [ ${MODE} = "dev" ]; then
        while getopts ":lt" OPT; do
            case ${OPT} in
                l)
                    LOCAL=1
                    ;;
                t)
                    TESTING=1
                    ;;
                \?)
                    echo "Invalid option: -$OPTARG" >&2
            esac
        done
        echo "running dev; local ${LOCAL}; testing ${TESTING}"
    elif [ ${MODE} = "staging" ]; then
        echo "running staging"
    elif [ ${MODE} = "prod" ]; then
        echo "running production"
    else
        echo "Invalid mode provided: dev|staging|prod" >&2
    fi
else
    echo "Provide one argument: dev|staging|prod" >&2
fi


#dev: local|aws testing|not
#prod: none
#staging: none

#    for OPTION in "${OPTIONS[@]}"; do
#        if [ ${ENV_ARG} = ${OPTION} ]; then
#            VALID=1
#        fi
#    done
#
#    if [ ${VALID} = 1 ]; then
#        echo "launching app on ${ENV_ARG}..."
#        export APP_ENV=${ENV_ARG}
#        export FLASK_APP=application.py
#        flask run
#    else
#        echo "${ENV_ARG} not a valid environment."
#    fi

#run -lt dev --> run dev branch, local, debug, testing
#run -l dev --> run dev branch, local, debug
#run -t dev --> run dev branch, aws staging instance, testing
#run dev --> run dev branch, aws staging instance
#run staging --> run staging branch, aws staging instance
#run prod --> run prod branch, aws production instance








