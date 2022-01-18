#!/bin/bash
#
# Copyright IBM Corp All Rights Reserved
#
# SPDX-License-Identifier: Apache-2.0
#
# Exit on first error
set -e

export MSYS_NO_PATHCONV=1
starttime=$(date +%s)
FABRIC_PATH="../fabric-samples/"
REPO_PATH="../"

# clean out any old identites in the wallets
rm -rf ${REPO_PATH}hlf_application/application-javascript/wallet/*

# launch network; create channel and join peer to channel
pushd ${FABRIC_PATH}test-network
./network.sh down
popd
