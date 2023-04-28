#!/bin/bash
set -e
if [ $# -eq 0 ]
then
	echo "Syntax: bash DockerFileCreator.sh IMAGE_NAME <OUTPUT_FILENAME>"
	exit 1;
fi
IMAGE_NAME=$1;
IMAGE_ID=$(sudo docker images $1 --format="{{.ID}}")
check=$(echo $IMAGE_ID| wc -w)
if [ $check -ne 1 ] 
then 
    echo "("$check") Images Found"
    echo "Please provide a valid docker image name";
    exit 1;
fi

if [ ! -z $2 ] 
then 
    OUTPUTFILE=$2
else
    OUTPUTFILE="Dockerfile"
fi
echo "Chosen default Output filename="$OUTPUTFILE



echo "Creating Dockerfile for IMAGEID="$IMAGE_ID
sudo docker history --no-trunc $IMAGE_ID  | tac | tr -s ' ' | cut -d " " -f 5- | sed 's,^/bin/sh -c #(nop) ,,g' | sed 's,^/bin/sh -c,RUN,g' | sed 's, && ,\n  & ,g' | sed 's,\s*[0-9]*[\.]*[0-9]*\s*[kMG]*B\s*$,,g' | head -n -1 > $2
