FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN rm -rf node_modules package-lock.json
RUN npm install --legacy-peer-deps
COPY . .
ENV CI=false
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
change 20
change 3
change 14
change 14
