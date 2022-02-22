# Update sister repository
if [ "$1" != "" ] && [ "$1" != "-r" ] && [ "$1" != "--run" ]; then
    echo "usage: update_public.sh [-r|--run]" >&2
    echo "       without the parameter -r/--run, a dry-run will be executed instead" >&2
    exit 1
fi
if [ "$1" == "-r" ] || [ "$1" == "--run" ]; then
    dry=N
else
    dry=Y
fi

set -eu

function stackd { pushd "$1" > /dev/null; }
function destackd { popd &> /dev/null; }

script_dir=$(dirname "$0")
target_dir="../cookadream_public"

stackd "$script_dir"
function finish {
    while destackd; do :; done
}
trap finish EXIT

commit="$(git log -n 1 --pretty=format:'%H')"

stackd "$target_dir"
git fetch --tags
version="$(git describe --tags --abbrev=0)"
# commit="$(git rev-list -n 1 "$version")"
destackd

if [ "$dry" == "N" ]; then
    output="src/cookadream/utils/version_info.py"
else
    output="/dev/stdout"
fi
{
    echo "PRODUCT_VERSION = '$version'"
    echo "PRODUCT_COMMIT = '$commit'"
} > "$output"
