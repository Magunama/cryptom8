#
# Build stage
#
FROM node:14.17.6 as build
WORKDIR /home/app
COPY ./ /home/app/
RUN npm install
RUN npm run build

#
# Package stage
#
FROM nginx:latest
COPY --from=build /home/app/dist/bachf /usr/share/nginx/html
#COPY --from=build /home/app/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
