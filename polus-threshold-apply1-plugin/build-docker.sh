#!/bin/bash

version=$(<VERSION)
docker build . -t labshare/polus-threshold-apply1-plugin:${version}