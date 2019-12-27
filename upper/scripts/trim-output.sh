#!/usr/bin/env bash

while IFS= read -r line; do
  grep $line ${2} | head -${3}
done < "$1"
