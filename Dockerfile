# the harness image: the code is baked in at /app/harness, in a different container from the repo it edits
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker
WORKDIR /app/harness
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "/app/harness/agent.py"]
