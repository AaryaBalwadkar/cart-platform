FROM alpine:3.22

RUN apk add --no-cache busybox-extras
WORKDIR /www
COPY index.html /www/index.html

EXPOSE 80
CMD ["sh", "-c", "echo 'Shopping Cart Active'; exec httpd -f -p 80 -h /www"]
