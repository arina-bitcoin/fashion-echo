# Этап сборки - подготовка статических файлов
FROM node:18-alpine AS builder

WORKDIR /app

# Копируем исходные файлы
COPY src/ ./src/

# Минификация и оптимизация (если нужно)
RUN apk add --no-cache minify && \
    mkdir -p dist && \
    cp -r src/* dist/ && \
    find dist -name "*.css" -exec minify {} -o {} \; && \
    find dist -name "*.js" -exec minify {} -o {} \; && \
    find dist -name "*.html" -exec minify --html-keep-document-tags {} -o {} \;

# Финальный этап - nginx с оптимизированными файлами
FROM nginx:alpine

# Создаем непривилегированного пользователя
RUN addgroup -g 1001 -S nginx-user && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx-user -g nginx-user nginx-user

# Копируем оптимизированные файлы
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем кастомную конфигурацию nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Устанавливаем права доступа
RUN chown -R nginx-user:nginx-user /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /var/cache/nginx && \
    chown -R nginx-user:nginx-user /var/log/nginx && \
    chown -R nginx-user:nginx-user /etc/nginx/conf.d

# Создаем директории для nginx с правильными правами
RUN touch /var/run/nginx.pid && \
    chown nginx-user:nginx-user /var/run/nginx.pid

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Запускаем от имени непривилегированного пользователя
USER nginx-user

CMD ["nginx", "-g", "daemon off;"]
