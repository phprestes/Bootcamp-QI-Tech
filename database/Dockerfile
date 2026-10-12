FROM postgres:16

# initdb roda só quando o volume nasce (make reset para reaplicar).
COPY database.sql /docker-entrypoint-initdb.d/01.sql
