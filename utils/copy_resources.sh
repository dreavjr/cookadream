#!/bin/bash
# copy model weights from private repo onto public repo prior to packaging

dry=Y
verbose_option=""
target_system=none
parameters=" macos windows linux -r --run -v --verbose "
target_systems=" macos windows linux "

while [ "$1" != "" ]; do
    if echo "$parameters" | grep -Fqv " $1 "; then
        echo "usage: copy_resources.sh <macos|windows|linux> [-r|--run] [-v|--verbose]" >&2
        echo "       without the parameter -r/--run, a dry-run will be executed instead" >&2
        echo "       copy resources from private repo to public repo for the specified system" >&2
        exit 1
    fi
    if [ "$1" == "-r" ] || [ "$1" == "--run" ]; then
        dry=N
    elif [ "$1" == "-v" ] || [ "$1" == "--verbose" ]; then
        verbose_option="-v"
    elif echo "$target_systems" | grep -Fqw "$1"; then
        if [ "$target_system" == "none" ]; then
            target_system="$1"
        else
            echo "only one target system should be specified" >&2
            exit 1
        fi
    fi
    shift
done

if [ "$target_system" == "none" ]; then
    echo "one target system must be specified" >&2
    exit 1
fi

set -eu

base_dir="$(basename "$(pwd)")"
if [ -f "SOURCE_DIR_NAME" ]; then
    source_dir=$(cat SOURCE_DIR_NAME | tr -d ' \r\n')
else
    source_dir="${base_dir}_private"
fi
if [ -f "TARGET_DIR_NAME" ]; then
    target_dir=$(cat TARGET_DIR_NAME | tr -d ' \r\n')
else
    target_dir="${base_dir}_public"
fi

if [ ! -d "$source_dir" ] && [ ! -d "$target_dir" ]; then
    echo "Repository directories not found or not configured" >&2
    echo "Expected source (private) dir: '$source_dir'"  >&2
    echo "Expected target (public) dir:  '$target_dir'"  >&2
    echo "Use the files SOURCE_DIR_NAME and TARGET_DIR_NAME to override defaults."  >&2
    exit 1
fi

if [ "$dry" != "N" ]; then
    echo "DRY RUN: cp -cp" $verbose_option "${source_dir}/src/cookadream/resources/weights/"*.h5 "${target_dir}/src/cookadream/resources/weights/"
else
    cp -cp $verbose_option "${source_dir}/src/cookadream/resources/weights/"*.h5 "${target_dir}/src/cookadream/resources/weights/"
fi

if [ "$target_system" == "windows" ]; then
    if [ "$dry" != "N" ]; then
        echo "DRY RUN: cp -cp" $verbose_option "${source_dir}/src/cookadream/resources/libs/"*.dll "${target_dir}/src/cookadream/resources/libs/"
    else
        cp -cp $verbose_option "${source_dir}/src/cookadream/resources/libs/"*.dll "${target_dir}/src/cookadream/resources/libs/"
    fi
fi
