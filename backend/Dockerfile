FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# CPU-only torch first, from PyTorch's own index - avoids pip resolving the
# default CUDA build (which drags in multi-GB nvidia_* packages we don't need
# for embeddings on CPU, and reliably times out on a normal connection).
RUN pip install --no-cache-dir --timeout 120 --retries 5 \
    torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --timeout 120 --retries 5 -r requirements.txt

# Pre-bake the embedding model into the image so first-request latency (and
# demo-day download flakiness) is zero.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
