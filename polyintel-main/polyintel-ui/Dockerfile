FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 5173

# Start the development server (for development)
# For production, use: npm run preview
CMD ["npm", "run", "dev", "--", "--host"]
