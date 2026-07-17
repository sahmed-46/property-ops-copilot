FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
ENV VITE_API_BASE=
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .
COPY --from=frontend /frontend/dist ./frontend/dist

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT}"]
