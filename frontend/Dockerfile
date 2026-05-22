# Step 1: Build React static assets
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./
RUN npm run build

# Step 2: Serve using Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
