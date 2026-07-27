FROM python:3.12.13-slim-bookworm

WORKDIR /course

COPY . .

CMD ["python", "other/tools/check_all.py"]
