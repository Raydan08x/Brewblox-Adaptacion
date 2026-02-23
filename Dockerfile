# --- Build Stage ---
FROM node:20-alpine AS build-stage

WORKDIR /app

# Install dependencies (using cache)
COPY package.json yarn.lock ./
RUN corepack enable && yarn install

# Copy source and build
COPY . .
RUN yarn build

# --- Production Stage ---
FROM nginx:alpine

# Copy built assets from build-stage
COPY --from=build-stage /app/dist /var/www/ui

# Nginx configuration
RUN printf "server { \n\
  listen 80 default_server; \n\
  root /var/www; \n\
  server_name brewblox; \n\
  access_log off; \n\
  absolute_redirect off; \n\
  sendfile on; \n\
  tcp_nopush on; \n\
  gzip on; \n\
  gzip_vary on; \n\
  gzip_types text/plain application/javascript application/x-javascript application/json text/javascript text/xml text/css image/svg+xml font/woff font/woff2; \n\
  location = / { \n\
  add_header used_location slash; \n\
  rewrite ^ /ui/index.html; \n\
  } \n\
  location = /ui { \n\
  add_header used_location slashui; \n\
  rewrite ^ /ui/index.html; \n\
  } \n\
  location = /ui/index.html { \n\
  expires 0; \n\
  add_header Pragma no-cache; \n\
  add_header Cache-Control 'no-cache, no-store, must-revalidate, proxy-revalidate, max-age=0'; \n\
  } \n\
  location ~* ^/ui/.*\\.(?:ico|css|js|svg|gif|jpe?g|png|woff2?)$ { \n\
  expires max; \n\
  add_header Pragma public; \n\
  add_header Cache-Control 'public, must-revalidate, proxy-revalidate'; \n\
  } \n\
  location /ui/ { \n\
  try_files \$uri \$uri.html /ui/index.html; \n\
  } \n\
  location /static/ { \n\
  autoindex on; \n\
  } \n\
  }\n" > /etc/nginx/conf.d/default.conf
