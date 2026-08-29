#!/usr/bin/env bash
set -euo pipefail

readonly DEPLOY_USER="tjcu8-deploy"
readonly SITE_ROOT="/var/www/tjcu8"
readonly INCOMING_DIR="$SITE_ROOT/incoming"
readonly RELEASES_DIR="$SITE_ROOT/releases"
readonly CURRENT_LINK="$SITE_ROOT/current"
readonly SITE_URL="https://tjcu8.elma-gohan.xyz/"

fail() {
    printf 'deploy error: %s\n' "$*" >&2
    exit 1
}

[[ "$(id -un)" == "$DEPLOY_USER" ]] || fail "run as $DEPLOY_USER"
[[ $# -eq 1 ]] || fail "usage: deploy-tjcu8 <release-id>"

release_id="$1"
[[ "$release_id" =~ ^[0-9a-f]{12}-[1-9][0-9]*$ ]] || fail "invalid release id"

archive="$INCOMING_DIR/$release_id.tar.gz"
checksum_file="$archive.sha256"
release_dir="$RELEASES_DIR/$release_id"
new_link="$SITE_ROOT/current.new"

exec 9>"$SITE_ROOT/deploy.lock"
flock -n 9 || fail "another deployment is running"

[[ -f "$archive" ]] || fail "archive is missing"
[[ -f "$checksum_file" ]] || fail "checksum is missing"
[[ ! -e "$release_dir" ]] || fail "release already exists"
[[ ! -e "$new_link" ]] || fail "stale current.new link exists"

expected_sha="$(tr -d '[:space:]' < "$checksum_file")"
[[ "$expected_sha" =~ ^[0-9a-f]{64}$ ]] || fail "invalid checksum"
actual_sha="$(sha256sum "$archive" | awk '{print $1}')"
[[ "$actual_sha" == "$expected_sha" ]] || fail "checksum mismatch"

while IFS= read -r entry; do
    [[ "$entry" != /* ]] || fail "absolute archive path"
    [[ "/$entry/" != *"/../"* ]] || fail "archive path traversal"
    case "$entry" in
        index.html|css|css/*|js|js/*|pages|pages/*|image|image/*) ;;
        *) fail "unexpected archive entry: $entry" ;;
    esac
done < <(tar -tzf "$archive")

previous_release=""
if [[ -L "$CURRENT_LINK" ]]; then
    previous_release="$(readlink -f "$CURRENT_LINK")"
fi

mkdir "$release_dir"
tar -xzf "$archive" -C "$release_dir"
find "$release_dir" -type d -exec chmod 0755 {} +
find "$release_dir" -type f -exec chmod 0644 {} +
[[ -f "$release_dir/index.html" ]] || fail "homepage is missing"
[[ -f "$release_dir/pages/json/image_index.json" ]] || fail "image index is missing"

ln -s "$release_dir" "$new_link"
mv -Tf "$new_link" "$CURRENT_LINK"

site_ready=false
for _ in {1..10}; do
    if page="$(curl --fail --silent --show-error \
        --resolve tjcu8.elma-gohan.xyz:443:127.0.0.1 \
        "$SITE_URL")" && grep -q '<title>呼气之窝</title>' <<< "$page"; then
        site_ready=true
        break
    fi
    sleep 1
done

if [[ "$site_ready" != true ]]; then
    if [[ -n "$previous_release" ]]; then
        ln -s "$previous_release" "$new_link"
        mv -Tf "$new_link" "$CURRENT_LINK"
    else
        rm -f "$CURRENT_LINK"
    fi
    fail "site verification failed; previous release restored"
fi

rm -f "$archive" "$checksum_file"
printf 'deployed release=%s sha256=%s previous=%s\n' \
    "$release_id" "$actual_sha" "${previous_release:-none}"
