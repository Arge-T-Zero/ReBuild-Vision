# ReBuild Vision — web arayüzü
#
# Çok aşamalı: derleme Node ile yapılır, yayın nginx ile. Son imajda
# node_modules ve kaynak kod bulunmaz.

FROM node:22-alpine AS derleme

WORKDIR /derleme

# Bağımlılıklar kilit dosyasından kurulur — sürümler birebir sabit.
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ ./
RUN npm run build


FROM nginx:1.27-alpine

COPY --from=derleme /derleme/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
