FROM ubuntu:latest
LABEL authors="majestic"

ENTRYPOINT ["top", "-b"]