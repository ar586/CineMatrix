FROM node:20-alpine

WORKDIR /app

# Install dependencies (copy package.json first)
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# Expose port
EXPOSE 4000

# Start app
CMD ["npm", "start", "--", "-p", "4000"]
