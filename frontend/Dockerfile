FROM node:20-alpine

WORKDIR /app

# Install dependencies first (cache-friendly layer)
COPY package.json package-lock.json* ./
RUN npm install

# Copy application source
COPY . .

# CRA dev server port
EXPOSE 3000

# Start the React dev server
CMD ["npm", "start"]
