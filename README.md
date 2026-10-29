This repo is best read by [commits](https://github.com/keith-shep/the-simplest-agent/commits/main/). 

```
set `ANTHROPIC_API_KEY` and `REPO_PATH` in `.env`

```

```bash
docker compose build
docker compose run --rm harness   # starts the agent on REPO_PATH, mounted at /app/repo
```

To watch each request and response in a second terminal:

```bash
python agent.py --debug
```