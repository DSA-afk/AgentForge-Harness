FROM ubuntu:latest
LABEL authors="maxaa"

ENTRYPOINT ["top", "-b"]