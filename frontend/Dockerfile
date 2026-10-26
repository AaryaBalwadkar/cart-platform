FROM alpine:3.22

RUN apk add --no-cache nginx
COPY nginx.conf /etc/nginx/http.d/default.conf
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
CMD ["sh", "-c", "echo 'Shopping Cart Active'; exec nginx -g 'daemon off;'"]
