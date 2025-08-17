FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Install prerequisites and wkhtmltopdf manually
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb -O /tmp/wkhtmltox.deb \
    && apt-get update \
    && apt-get install -y /tmp/wkhtmltox.deb \
    && rm /tmp/wkhtmltox.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ARG GEMINI_API_KEY
ARG TAVILY_API_KEY

RUN --mount=type=secret,id=GEMINI_API_KEY,mode=0444,required=true \
    export GROQ_API_KEY=$(cat /run/secrets/GEMINI_API_KEY) && \
    echo "GEMINI_API_KEY is set."

RUN --mount=type=secret,id=TAVILY_API_KEY,mode=0444,required=true \
    export TAVILY_API_KEY=$(cat /run/secrets/TAVILY_API_KEY) && \
    echo "TAVILY_API_KEY is set."

ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV TAVILY_API_KEY=${TAVILY_API_KEY}

CMD ["python", "main.py"]