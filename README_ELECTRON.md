# Gmail RAG Assistant - Electron Migration

This project has been successfully migrated from PyQt6 to Electron while preserving the Python backend functionality.

## 🚀 New Architecture

- **Frontend**: Modern Electron-based UI with HTML/CSS/JavaScript
- **Backend**: Python Flask API server (unchanged RAG functionality)
- **Communication**: REST API between frontend and backend

## 📁 Project Structure

```
Gmail RAG Assistant/
├── frontend/                 # Electron frontend
│   ├── index.html           # Main UI
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript modules
│   └── assets/              # Static assets
├── electron/                # Electron main process
│   ├── main.js             # Electron main process
│   └── preload.js          # Secure IPC bridge
├── ui/                      # Legacy PyQt6 UI (preserved)
├── backend_server.py        # Flask API server
├── RAG_Gmail.py            # Core RAG functionality (unchanged)
├── main.py                 # New launcher with interface selection
├── main_electron.py        # Electron launcher
├── main_pyqt6.py          # Legacy PyQt6 launcher
├── package.json            # Node.js dependencies
└── requirements.txt        # Python dependencies (updated)
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

#### Python Dependencies
```bash
pip install -r requirements.txt
```

#### Node.js Dependencies (for Electron)
```bash
npm install
```

### 2. Configure API Keys

1. **Gmail API**: Place `credentials.json` in the root directory
2. **Groq API**: Set in `.env` file or through the Settings interface

### 3. Launch the Application

#### Option 1: Interactive Launcher (Recommended)
```bash
python main.py
```
Choose from:
- 🎨 Electron (Modern, Recommended)
- 🖥️ PyQt6 (Legacy)
- 🌐 Web Browser Only

#### Option 2: Direct Launch
```bash
# Electron interface
python main.py --electron

# PyQt6 interface (legacy)
python main.py --pyqt6

# Web interface only
python main.py --web

# Auto-detect best interface
python main.py --auto
```

## ✨ New Features (Electron Interface)

### Modern UI/UX
- Responsive design with dark theme
- Smooth animations and transitions
- Modern typography and spacing
- Better accessibility support

### Enhanced Functionality
- Real-time connection status monitoring
- Improved error handling and user feedback
- Better keyboard shortcuts
- Enhanced search and filtering
- Modal dialogs for detailed email viewing

### Technical Improvements
- Faster startup time
- Better resource management
- Cross-platform compatibility
- Modern web technologies (HTML5, CSS3, ES6+)
- Secure IPC communication

## 🔄 Migration Benefits

1. **Modern Interface**: Contemporary design with improved UX
2. **Better Performance**: Optimized resource usage
3. **Cross-Platform**: Consistent experience across OS
4. **Maintainability**: Easier to update and extend
5. **Web Compatibility**: Fallback to browser if Electron unavailable

## 🔧 Development

### Frontend Development
```bash
# Start Electron in development mode
npm run dev

# Build for production
npm run build
```

### Backend Development
The Python backend remains unchanged. All RAG functionality is preserved:
- Email loading and processing
- Vector search with FAISS
- AI chat with Groq LLM
- Gmail API integration

## 📝 API Endpoints

The Flask backend exposes these REST endpoints:

- `GET /api/health` - Health check
- `POST /api/chat/message` - Send chat messages
- `POST /api/emails/load` - Load emails from Gmail
- `POST /api/emails/search` - Search emails
- `GET /api/system/status` - System status
- `GET/POST /api/config` - Configuration management

## 🔒 Security

- No direct Node.js access from renderer process
- Secure IPC communication through preload script
- API keys stored locally and encrypted
- CORS protection for backend API

## 🐛 Troubleshooting

### Common Issues

1. **Electron won't start**: Install Node.js and run `npm install`
2. **PyQt6 errors**: Install PyQt6 with `pip install PyQt6`
3. **Backend API errors**: Check Python dependencies and API keys
4. **Connection issues**: Verify internet connection and firewall settings

### Fallback Options

If Electron fails to start, the application automatically falls back to:
1. Web interface in browser
2. PyQt6 interface (if available)

## 🎯 Future Enhancements

- [ ] Light theme support
- [ ] Additional AI model integrations
- [ ] Enhanced email filtering
- [ ] Real-time notifications
- [ ] Export/import functionality
- [ ] Mobile-responsive web interface

## 📄 License

This project maintains the same license as the original codebase.

---

**Note**: The original PyQt6 interface is preserved and can still be used by selecting the PyQt6 option in the launcher or running `python main_pyqt6.py` directly.