FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    xvfb \
    xfonts-75dpi \
    xfonts-base \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

ARG GEMINI_API_KEY
RUN --mount=type=secret,id=GEMINI_API_KEY,mode=0444,required=true \
    export GROQ_API_KEY=$(cat /run/secrets/GEMINI_API_KEY) && \
    echo "GEMINI_API_KEY is set."

ENV GEMINI_API_KEY=${GEMINI_API_KEY}

CMD ["python", "main.py"]
