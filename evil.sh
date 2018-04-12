#!/bin/bash

if [ $# -eq 0 ]
then 
	echo "Default ten evil clients"
	Num=10
else
	Num=$1
fi

for ((i=1; i<=Num; ++i))
do
	gnome-terminal --tab -e "python evilClient.py localhost 8080" 
done

