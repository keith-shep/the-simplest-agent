## Corrected Mental Model

What actually happens:
- Each time we submit an input, its actually being appended to a list of the whole conversation.
- The model is **stateless** and does not "remember" between turns.
```json
😃
[
    { 
        "role": "user", 
        "content": "what is the answer to life, the universe and everything?" 
    }
]
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
[
    { 
        "role": "user", 
        "content": "what is the answer to life, the universe and everything?" 
    },
    { 
        "role": "assistant", 
        "content": "42" 
    },
    { 
        "role": "user", 
        "content": "how did you determine that?"
    }
]
```

<p align="center">↓</p>

```json
🤖
{ 
    "role": "assistant", 
    "content": "it was from the book the Hitchhiker's Guide to the Galaxy." 
}
```