#!/bin/bash

ID="$(ota send report.json --local)"

echo $ID

ota download "${ID}" pdf --local