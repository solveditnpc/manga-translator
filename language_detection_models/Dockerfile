FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential wget
RUN mkdir -p /app/models && \
    wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz -O /app/models/lid.176.ftz
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "language_detect.py"]