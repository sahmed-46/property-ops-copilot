FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
ENV VITE_API_BASE=
RUN npm run build && test -f dist/index.html

FROM python:3.12-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .
COPY --from=frontend /frontend/dist ./frontend/dist
RUN test -f frontend/dist/index.html
ARG BUILD_SHA=dev
RUN echo "Build SHA: ${BUILD_SHA}"

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT}"]
