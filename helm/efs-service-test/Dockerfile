FROM alpine:3.19.0

# make a pipe fail on the first failure
SHELL ["/bin/sh", "-o", "pipefail", "-c"]

# ensure we only use apk repositories over HTTPS (altough APK contain an embedded signature)
RUN echo "https://alpine.global.ssl.fastly.net/alpine/v$(cut -d . -f 1,2 < /etc/alpine-release)/main" > /etc/apk/repositories \
    && echo "https://alpine.global.ssl.fastly.net/alpine/v$(cut -d . -f 1,2 < /etc/alpine-release)/community" >> /etc/apk/repositories

RUN apk -v --no-cache --update add ca-certificates \
    grep \
    fio \
    && rm -rf /var/cache/apk/*

