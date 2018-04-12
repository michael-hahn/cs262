#!/bin/sh

gnome-terminal -e "python evilClient.py localhost 8080" --tab -e "python evilClient.py localhost 8080"
