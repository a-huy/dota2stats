#!/bin/bash

while true
do
    ls ./players/all/$1 | wc -l
    sleep 60
done

