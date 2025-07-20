# 🧠 Smart Claims Processing Platform

An AI-powered platform to analyze insurance claim documents (PDFs, images, and text) using Google's Gemini API. Automatically extracts claim data, classifies type/priority, checks policy compliance, and summarizes the claim.

---

## 🚀 Features

- Upload **PDF, PNG, JPG, or TXT** claim documents
- Auto-extract:
  - Claimant name
  - Claim amount & date
  - Damages, policy number, and description
- Classify claim type and priority
- Assess **policy compliance**
- Summarize the claim in natural language

---

## 🛠️ Setup Instructions (VS Code)

### 1. Clone the Repository

```bash
git clone https://github.com/Avi112005/Smart-Claims-Processing-Platform.git
cd Smart-Claims-Processing-Platform
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Your Gemini API Key
Create a .env file:
```bash
GEMINI_API_KEY=AIzaSyChXOYoFcK-aSpqAMzw0tC-xjYcurFloeA
```