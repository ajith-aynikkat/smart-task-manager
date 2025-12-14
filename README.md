# 🚀 Smart Task Manager – End-to-End DevOps CI/CD Project

This repository documents a **complete DevOps lifecycle** starting from local development to **fully automated deployment using Docker, Docker Compose, and Jenkins**.

---

## 📌 Project Objectives

- Create a structured application
- Secure secrets using `.env`
- Containerize using Docker
- Deploy using Docker Compose
- Automate build & deployment using Jenkins
- Trigger deployment automatically on Git push

---

## 🛠️ Tech Stack Used

- Git & GitHub
- Docker
- Docker Compose
- Jenkins (Docker-based)
- Linux (Ubuntu EC2)
- Environment variables (`.env`)

---

## 📁 Project Structure

```text
smart-task-manager/
├── Dockerfile
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── js/
│   │   └── app.js
│   └── pages/
│       ├── login.html
│       ├── dashboard.html
│       └── tasks.html
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Jenkinsfile
└── README.md
```

---

# 🧑‍💻 PART 1: Local Project Setup

### 1️⃣ Create Project Directory
```bash
mkdir smart-task-manager
cd smart-task-manager
```

---

### 2️⃣ Create Folder Structure
```bash
mkdir backend frontend
mkdir -p frontend/js frontend/pages
touch Dockerfile docker-compose.yml Jenkinsfile README.md .gitignore .env.example
```

---

### 3️⃣ Configure `.gitignore`
```bash
nano .gitignore
```

```gitignore
.env
__pycache__/
node_modules/
```

---

### 4️⃣ Create Environment Template
```bash
nano .env.example
```

```env
APP_PORT=5000
DB_HOST=database
DB_USER=admin
DB_PASSWORD=admin123
```

---

### 5️⃣ Backend Application Setup
```bash
cd backend
nano app.py
```

```python
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Smart Task Manager Backend is running!"

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("APP_PORT", 5000))
```

```bash
nano requirements.txt
```

```text
flask
```

```bash
nano Dockerfile
```

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

### 6️⃣ Frontend Application Setup (Nginx Based)

```bash
cd ../frontend
nano nginx.conf
```

```nginx
server {
    listen 80;
    root /usr/share/nginx/html/pages;
    index login.html;

    location / {
        try_files $uri $uri/ /login.html;
    }
}
```

```bash
nano js/app.js
```

```javascript
console.log("Smart Task Manager frontend loaded");
```

```bash
nano pages/login.html
```

```html
<!DOCTYPE html>
<html>
<head>
  <title>Login</title>
</head>
<body>
  <h2>Login Page</h2>
</body>
</html>
```

```bash
nano pages/dashboard.html
```

```html
<!DOCTYPE html>
<html>
<head>
  <title>Dashboard</title>
</head>
<body>
  <h2>Dashboard</h2>
</body>
</html>
```

```bash
nano pages/tasks.html
```

```html
<!DOCTYPE html>
<html>
<head>
  <title>Tasks</title>
</head>
<body>
  <h2>Tasks Page</h2>
</body>
</html>
```

```bash
nano Dockerfile
```

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY pages /usr/share/nginx/html/pages
COPY js /usr/share/nginx/html/js
```

---

### 7️⃣ Docker Compose Configuration
```bash
cd ..
nano docker-compose.yml
```

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    env_file:
      - .env
    ports:
      - "5000:5000"

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
```

---

# 📤 PART 2: Git Version Control

### 8️⃣ Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial project setup"
```

---

### 9️⃣ Push Code to GitHub (Securely)
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/smart-task-manager.git
git push -u origin main
```

✅ `.env` is never pushed to GitHub

---

# ☁️ PART 3: Remote Host Setup (EC2 / VM)

### 1️⃣ Connect to Server
```bash
ssh -i key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

### 2️⃣ Install Required Software
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
```

---

### 3️⃣ Clone Project Repository
```bash
git clone https://github.com/<your-username>/smart-task-manager.git
cd smart-task-manager
```

---

### 4️⃣ Create `.env` File on Server
```bash
nano .env
```

```env
APP_PORT=5000
DB_HOST=database
DB_USER=admin
DB_PASSWORD=admin123
```

---

### 5️⃣ Build & Run Application
```bash
docker compose up -d --build
```

---

### 6️⃣ Verify Containers & Logs
```bash
docker ps
docker logs <container_name>
```

Application URLs:
- Frontend → `http://<EC2_PUBLIC_IP>:8080`
- Backend → `http://<EC2_PUBLIC_IP>:5000`

---

# 🤖 PART 4: Jenkins CI/CD Automation

### 1️⃣ Run Jenkins with Docker Support
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  jenkins-with-docker
```

---

### 2️⃣ Jenkins Pipeline Script (`Jenkinsfile`)
```groovy
pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Build & Deploy') {
      steps {
        sh 'docker compose up -d --build'
      }
    }
  }
}
```

---

### 3️⃣ Configure Jenkins Job
- Create **Pipeline Job**
- Select **Pipeline script from SCM**
- Repository URL: GitHub repo
- Branch: `main`
- Script Path: `Jenkinsfile`

---

### 4️⃣ Enable GitHub Webhook
Payload URL:
```
http://<EC2_PUBLIC_IP>:8080/github-webhook/
```

Enable:
✔ GitHub hook trigger for GITScm polling

---

# 🔁 PART 5: Automation Test

```bash
echo "# CI trigger" >> README.md
git add .
git commit -m "Trigger Jenkins pipeline"
git push origin main
```

✔ Jenkins starts automatically  
✔ Application rebuilds & redeploys  

---

# ✅ Final Validation

```bash
docker ps
```

Jenkins Console Output:
```
Finished: SUCCESS
```

---

## 🧠 Key Learnings
- Secure environment handling with `.env`
- Docker & Docker Compose orchestration
- Jenkins CI/CD automation
- Real-world DevOps workflow

---

## 🏁 Conclusion
This project demonstrates a **complete DevOps CI/CD pipeline** suitable for beginners, interviews, and real-world practice.

⭐ If you found this helpful, give the repository a star!
