#!/usr/bin/env bash
# check-orphans.sh — verify no DevOps-track GCP resources linger after teardown.
# Usage: GOOGLE_CLOUD_PROJECT=future-abode-338616 ./check-orphans.sh <name-substring>
# Exits 0 if clean, 1 if any matching resource found.
set -u
P="${GOOGLE_CLOUD_PROJECT:-future-abode-338616}"
SUB="${1:-sshsetup-vm}"
G="gcloud"
found=0
check() { # $1 = command, $2 = label
  out=$($G $1 2>/dev/null | grep -i "$SUB")
  if [ -n "$out" ]; then echo "ORPHAN [$2]: $out"; found=1; fi
}
check "compute instances list --project=$P" instances
check "compute firewalls list --project=$P" firewalls
check "dns managed-zones list --project=$P" dns
check "storage ls --project=$P" buckets
if [ "$found" -eq 0 ]; then echo "CLEAN: no resources matching '$SUB' in $P"; exit 0; fi
exit 1
