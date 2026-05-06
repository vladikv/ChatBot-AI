# 🤖 Order Support Chatbot

> A full-stack AI-powered customer support chatbot with user authentication, order management, and request logging.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔐 **Auth System** | Register & login with bcrypt-hashed passwords |
| 📦 **Order Management** | Check status, cancel orders, list all orders |
| 🤖 **AI Responses** | Google Gemini 2.5 Flash for open-ended questions |
| 📋 **Request Logging** | Every message saved to DB with user & timestamp |
| 🛡️ **API Protection** | API key middleware on all chat endpoints |
| 🎨 **Clean Frontend** | Separate HTML / CSS / JS, no frameworks |

---

## 🖥️ Screenshots

> **Login Screen**
>
> <img width="448" height="387" alt="image" src="https://github.com/user-attachments/assets/ca862eab-b75b-43dc-82e1-d96902afc655" />


> **Chat Interface**
>
> <img width="496" height="627" alt="image" src="https://github.com/user-attachments/assets/8c9749e9-ac3c-49ba-984e-ca5f899f18c0" />


> **Database Logs**
>
> <img width="978" height="167" alt="image" src="https://github.com/user-attachments/assets/c16e1ec5-56ec-4418-a9f9-684f4d7fc947" />


---

## 💬 Chat Commands

| Command | Example | Result |
|---------|---------|--------|
| Check order status | `status of order 123` | Returns current status |
| Cancel an order | `cancel order 456` | Cancels the order |
| List all orders | `show all orders` | Lists every order |
| Anything else | `what is photosynthesis?` | AI-powered response |

---

## 🗂️ Project Structure

```
order-chatbot/
├── app.py                  # Backend — Flask routes, DB, AI logic
├── templates/
│   └── index.html          # Frontend HTML
└── static/
    ├── style.css            # Styles
    └── script.js            # Frontend logic (auth, chat, API calls)
```

---

## 🔒 Security

- Passwords hashed with **bcrypt** — never stored as plain text
- **Parameterized SQL queries** — protection against SQL injection
- **API key middleware** — all `/chat` requests require a valid key
- **Environment variables** — no sensitive data hardcoded in source

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | MariaDB |
| AI | Google Gemini 2.5 Flash |
| Auth | Flask Sessions + bcrypt |
| Frontend | HTML, CSS, JS |

