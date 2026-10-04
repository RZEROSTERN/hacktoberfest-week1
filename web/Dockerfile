FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-slim
WORKDIR /app
COPY --from=build /app/.output ./.output
ENV HOST=0.0.0.0 PORT=3000 NODE_ENV=production
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
