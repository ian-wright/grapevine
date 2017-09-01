#!/usr/bin/env bash

#echo "arg 1: $1"
#echo "arg 2: $2"
#
#MODE=$1
#LOCAL=0
#TESTING=0
#
#if [ $# -eq 2 ]; then
#    if [ ${MODE} = "dev" ]; then
#        while getopts ":lt" OPT; do
#            case ${OPT} in
#                l)
#                    LOCAL=1
#                    ;;
#                t)
#                    TESTING=1
#                    ;;
#                \?)
#                    echo "Invalid option: -$OPTARG" >&2
#            esac
#        done
#        echo "running dev; local ${LOCAL}; testing ${TESTING}"
#    elif [ ${MODE} = "staging" ]; then
#        echo "running staging"
#    elif [ ${MODE} = "prod" ]; then
#        echo "running production"
#    else
#        echo "Invalid mode provided: dev|staging|prod" >&2
#    fi
#else
#    echo "Provide one argument: dev|staging|prod" >&2
#fi


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

#run -m dev -lt --> run dev branch, local, debug, testing
#run -m dev -l --> run dev branch, local, debug
#run -m dev -t --> run dev branch, aws staging instance, testing
#run -m dev --> run dev branch, aws staging instance
#run -m staging --> run prod branch, aws staging instance
#run -m prod --> run prod branch, aws production instance


LOCAL=0
TESTING=0

# parse all args
while getopts ":m:lt" opt; do
    case ${opt} in
        m)
            if [ ${OPTARG} == dev ]; then
                echo "dev mode enabled"
                MODE=dev
            elif [ ${OPTARG} == staging ]; then
                echo "staging mode enabled"
                MODE=stage
            elif [ ${OPTARG} == production ]; then
                echo "production mode enabled"
                MODE=prod
            else
                echo "Invalid mode. (dev|staging|production)" >&2
                exit 1
            fi
            ;;
        l)
            echo "local mode enabled"
            LOCAL=1
            ;;
        t)
            echo "testing mode enabled"
            TESTING=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

export FLASK_APP=application.py

if [ ${MODE} == "dev" ]; then
    if [ ${LOCAL} -eq 1 ]; then
        if [ ${TESTING} -eq 1 ]; then
            export APP_ENV=loctest
        else
            export APP_ENV=loc
        fi
        echo "launching flask app locally..."
        flask run
    else
        if [ ${TESTING} -eq 1 ]; then
            #export APP_ENV=awsdevtest
            echo "aws devtest not set up yet" >&2
        else
            #export APP_ENV=awsdev
            echo "aws dev not set up yet" >&2
        fi
    fi
elif [ ${MODE} == stage ]; then
    echo "staging mode not set up yet" >&2
elif [ ${MODE} == prod ]; then
    echo "production mode not set up yet" >&2
else
    echo "Invalid mode. (dev|staging|production)" >&2
    exit 1
fi
