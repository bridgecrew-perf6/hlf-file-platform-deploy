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
CC_SRC_LANGUAGE="go"
CC_SRC_PATH="../../chaincodes/"

# clean out any old identites in the wallets
rm -rf ${REPO_PATH}hlf_application/application-javascript/wallet/*

pushd ${REPO_PATH}chaincodes/history
./build.sh
popd

# launch network; create channel and join peer to channel
pushd ${FABRIC_PATH}test-network
./network.sh down
./network.sh up createChannel -ca -s couchdb
./network.sh deployCC -ccn history -ccv 1 -cci Init -ccl ${CC_SRC_LANGUAGE} -ccp ${CC_SRC_PATH}history
popd

pushd ${REPO_PATH}hlf_application/application-javascript
node enrollAdmin.js
node registerUser.js
popd
