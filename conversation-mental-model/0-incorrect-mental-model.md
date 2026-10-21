# Incorrect Mental Modal

What we think happens:
- Each time we hit submit, we only send that input to the LLM.
```json
😃
{
  "role": "user",
  "content": "what is the answer to life, the universe and everything?"
}
```

<p align="center">↓</p>

```json
🤖
{
  "role": "assistant",
  "content": "42"
}
```

<p align="center">↓</p>

```json
😃
{
  "role": "user",
  "content": "how did you determine that?"
}
```

<p align="center">↓</p>

```json
🤖
{
  "role": "assistant",
  "content": "It was from the book - The Hitchhiker's Guide to the Galaxy."
}
```