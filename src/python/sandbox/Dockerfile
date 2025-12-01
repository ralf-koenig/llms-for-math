FROM python:3.11-slim

WORKDIR /sandbox

RUN pip install --no-cache-dir flask sympy numpy

COPY executor.py .

EXPOSE 8000

CMD ["python3", "executor.py"]
