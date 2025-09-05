# 🤖 Gmail RAG Assistant - Modern Desktop App

A beautiful, AI-powered desktop application that transforms how you interact with your Gmail emails using advanced RAG (Retrieval-Augmented Generation) technology.

![Gmail RAG Assistant](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![AI](https://img.shields.io/badge/AI-Groq%20LLM-orange.svg)
![Gmail API](https://img.shields.io/badge/Email-Gmail%20API-red.svg)

## ✨ Features

### 🎨 **Modern Beautiful UI**
- **Dark/Light Themes** - Professional Material Design-inspired interface
- **Responsive Layout** - Sidebar navigation with resizable panels
- **Smooth Animations** - Polished transitions and visual feedback
- **Chat Interface** - Modern message bubbles with typing indicators

### 🧠 **AI-Powered Capabilities**
- **Natural Language Queries** - Ask questions about your emails in plain English
- **Smart Email Search** - Vector-based semantic search through your email history
- **Intelligent Responses** - Context-aware answers using advanced LLM technology
- **Email Summarization** - Automatic email content analysis and summarization

### 🎤 **Voice & Accessibility**
- **Voice Input** - Speak your questions naturally
- **Text-to-Speech** - Listen to AI responses
- **Keyboard Shortcuts** - Efficient navigation and control
- **High DPI Support** - Crystal clear on all screen resolutions

### 📧 **Email Management**
- **Gmail Integration** - Secure OAuth2 authentication
- **Real-time Loading** - Background email synchronization
- **Advanced Filtering** - Search by content, sender, date, and more
- **Email Viewer** - Clean, readable email display with metadata

## 🚀 Quick Start

### 1. **Prerequisites**
- Python 3.8 or higher
- Gmail account with API access
- Groq API key (free at [console.groq.com](https://console.groq.com/))

### 2. **Installation**

```bash
# Clone or download the repository
cd email_Rag_app-main

# Install dependencies (automatic with launch script)
pip install -r requirements.txt
```

### 3. **Setup Gmail API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Desktop Application**
6. Download the JSON file and rename it to `credentials.json`
7. Place `credentials.json` in the app directory

### 4. **Setup Groq API**

1. Visit [Groq Console](https://console.groq.com/)
2. Create a free account
3. Generate an API key
4. Create a `.env` file in the app directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. **Launch the Application**

```bash
# Easy launch with automatic setup checks
python launch.py

# Or direct launch
python main.py
```

## 📋 Usage Guide

### 🎯 **Getting Started**

1. **First Launch** - The app will authenticate with Gmail (one-time setup)
2. **Load Emails** - Click "Load Emails" to sync your recent messages
3. **Start Chatting** - Ask questions about your emails in natural language

### 💬 **Example Queries**

```
"Show me emails from my bank this month"
"What did John say about the project deadline?"
"Summarize all emails about vacation requests"
"Find emails with attachments from last week"
"What meetings do I have scheduled?"
```

### 🔧 **Navigation**

- **💬 Chat** - AI conversation interface
- **📧 Emails** - Browse and search your email collection
- **⚙️ Settings** - Configure API keys, themes, and preferences
- **ℹ️ About** - Application information and credits

### 🎨 **Customization**

- **Themes** - Switch between Dark/Light modes in Settings
- **Font Size** - Adjust text size for better readability
- **Voice Settings** - Enable/disable text-to-speech and voice input
- **AI Model** - Choose different Groq models for responses

## 🏗️ Architecture

### **Modern Tech Stack**
- **Frontend**: PyQt6 with custom Material Design components
- **AI Engine**: Groq LLM with LangChain orchestration
- **Vector DB**: FAISS for local email embeddings
- **Email API**: Google Gmail API with OAuth2
- **Voice**: SpeechRecognition + pyttsx3

### **Key Components**
```
ui/
├── main_window.py      # Main application window
├── chat_interface.py   # AI chat component
├── email_management.py # Email browser and search
├── settings_interface.py # Configuration panel
├── components.py       # Reusable UI widgets
└── styles.py          # Modern theme system
```

## 🔒 Security & Privacy

- **Local Processing** - Emails are processed locally with FAISS
- **Secure Authentication** - OAuth2 for Gmail access
- **API Key Protection** - Credentials stored securely
- **No Data Sharing** - Your emails never leave your device
- **Open Source** - Transparent, auditable codebase

## 🐛 Troubleshooting

### **Common Issues**

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**Gmail authentication fails**
- Ensure `credentials.json` is in the correct location
- Check that Gmail API is enabled in Google Cloud Console

**Groq API errors**
- Verify your API key in the `.env` file
- Check your Groq account quota and usage

**Voice input not working**
- Check microphone permissions
- Install system audio dependencies if needed

### **Performance Tips**

- **RAM Usage**: FAISS loads email embeddings into memory
- **Email Limit**: Large email collections may take longer to process
- **Network**: Initial email loading requires internet connection
- **Storage**: Vector indices are cached locally for faster startup

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Questions**: Ask in GitHub Discussions
- **Updates**: Star the repo for notifications

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** - For providing fast, affordable LLM inference
- **Google** - For Gmail API access
- **PyQt6** - For the excellent desktop GUI framework
- **FAISS** - For efficient vector similarity search
- **OpenAI** - For inspiring the conversational AI approach

---

**Made with ❤️ by the Gmail RAG Assistant Team**

Transform your email experience today! 🚀✨# GmailRagBot
# RAG_BEAST
# ragbotplus
