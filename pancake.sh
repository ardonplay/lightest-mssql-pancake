#!/bin/bash

function usage() {
    cat <<USAGE

Usage:
    $0 [command] [options]

Commands:
    run          Run db
    stop 	 Stop db
    down         Delete all server
    drop         Drop database by name
    restore      Restore database from .bak file
    build        Build new image from src
Description:
    pancake - script for managing mssql server.

USAGE
    exit 1
}


PROJECT_DIR=$(dirname "$(realpath "$0")")

# ==============================================
# COMMAND SWITCHER

case $1 in
# run db
run)
    shift 1;
    while getopts "dh" opt; do
        case $opt in
        d) DETACHED=1 ;;
        \?) echo "Invalid option -$OPTARG"
            exit 1
             ;;
        esac
    done

    shift $((OPTIND - 1))

    if [[ $DETACHED ]]; then
        echo "STARTING..."
        docker compose -f  ${PROJECT_DIR}/src/docker/docker-compose.yml up -d
    else 
        docker compose -f  ${PROJECT_DIR}/src/docker/docker-compose.yml up
    fi
    ;;

# stop db
stop)
    shift 1;
    docker compose -f  ${PROJECT_DIR}/src/docker/docker-compose.yml stop
    ;;

down)
    shift 1;
    docker compose -f ${PROJECT_DIR}/src/docker/docker-compose.yml down
    ;;
drop)
    shift 1;
    database_name=$1
    docker exec -it lightest-mssql-pancake drop ${database_name}
    ;;
restore)
    shift 1;

    bak_file=$1
    db_name=$2
    file_name=$(basename "$bak_file")

    docker cp "$bak_file" "lightest-mssql-pancake:/var/backups/"
    docker exec -it --user root lightest-mssql-pancake  chmod 755 /var/backups/${file_name}
    docker exec -it lightest-mssql-pancake restore /var/backups/${file_name}
    
    ;;

build)
    shift 1;
    docker compose -f ${PROJECT_DIR}/src/docker/docker-compose.yml build
    ;;
# show help
--help)
    usage
    ;;
help)
    usage
    ;;
-h)
    usage
    ;;

# All invalid commands will invoke usage page
*)
    usage
    ;;
esac