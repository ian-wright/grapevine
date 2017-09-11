#!/usr/bin/env bash

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

if [ ${MODE} == "dev" ]; then
    if [ ${LOCAL} -eq 1 ]; then
        if [ ${TESTING} -eq 1 ]; then
            export APP_ENV=loctest
        else
            export APP_ENV=loc
        fi
        export FLASK_DEBUG=1
        export FLASK_APP=application.py
        echo "launching flask app locally..."
        flask run
    else
        if [ ${TESTING} -eq 1 ]; then
            eb setenv APP_ENV=awsdevtest
        else
            eb setenv APP_ENV=awsdev
        fi
        echo "deploying last commit on current branch to EB dev..."
        eb setenv FLASK_DEBUG=1
        eb deploy grapevine-dev
        eb open
    fi
elif [ ${MODE} == stage ]; then
    echo "staging mode not set up yet" >&2
elif [ ${MODE} == prod ]; then
    echo "production mode not set up yet" >&2
else
    echo "Invalid mode. (dev|staging|production)" >&2
    exit 1
fi
