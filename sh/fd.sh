#!/bin/bash

##auto fdisk disk and mkfs disk,delete 11 parts.

dev=$1'1'
echo "d

d

d

d

d

d

d

d

d

d

d

n




t
fd
w
" | fdisk $1
