#!/usr/bin/env python3
"""
Backend API Server for Gmail RAG Assistant
This server exposes the RAG_Gmail functionality via HTTP endpoints for the Electron frontend
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, Response, send_from_directory, send_file
from flask_cors import CORS
import traceback
from pathlib import Path

# Import our RAG Gmail functionality
from RAG_Gmail import ask_question, load_emails, Vector_Search, get_last_checked_time

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron frontend

# Configure static files for web fallback
frontend_dir = Path(__file__).parent / 'frontend'
if frontend_dir.exists():
    app.static_folder = str(frontend_dir)

# Global variables for managing conversation state
conversation_sessions = {}
current_session_id = None

def create_session_id():
    """Create a new session ID based on timestamp"""
    return f"session_{int(time.time() * 1000)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Gmail RAG Assistant Backend'
    })

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        session_id = data.get('session_id')
        
        # Get existing conversation or start new one
        messages = None
        if session_id and session_id in conversation_sessions:
            messages = conversation_sessions[session_id]
        
        # Process the message using RAG_Gmail
        try:
            updated_messages, response = ask_question(message, messages)
            
            # Create new session if needed
            if not session_id:
                session_id = create_session_id()
            
            # Store conversation state
            conversation_sessions[session_id] = updated_messages
            
            return jsonify({
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as rag_error:
            print(f"RAG processing error: {str(rag_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            
            return jsonify({
                'error': f'Failed to process your message: {str(rag_error)}',
                'details': 'Please check your API configuration and try again.'
            }), 500
        
    except Exception as e:
        print(f"Chat message error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/chat/session/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
            return jsonify({'message': 'Session deleted successfully'})
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete session: {str(e)}'}), 500

@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get list of active chat sessions"""
    try:
        sessions = []
        for session_id, messages in conversation_sessions.items():
            # Get first user message as session title
            title = "New Chat"
            if messages:
                for msg in messages:
                    if msg.get('role') == 'user':
                        title = msg.get('content', 'New Chat')[:50]
                        if len(msg.get('content', '')) > 50:
                            title += "..."
                        break
            
            sessions.append({
                'session_id': session_id,
                'title': title,
                'message_count': len([m for m in messages if m.get('role') in ['user', 'assistant']])
            })
        
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': f'Failed to get sessions: {str(e)}'}), 500

@app.route('/api/emails/load', methods=['POST'])
def load_emails_endpoint():
    """Load emails from Gmail"""
    try:
        print("Loading emails from Gmail...")
        
        # Run email loading in a separate thread to avoid blocking
        def load_emails_thread():
            try:
                load_emails()
                print("Emails loaded successfully")
            except Exception as e:
                print(f"Error loading emails: {str(e)}")
        
        thread = threading.Thread(target=load_emails_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Email loading started in background',
            'status': 'processing'
        })
        
    except Exception as e:
        print(f"Load emails error: {str(e)}")
        return jsonify({'error': f'Failed to start email loading: {str(e)}'}), 500

@app.route('/api/emails/search', methods=['POST'])
def search_emails():
    """Search emails using vector search"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        k = data.get('k', 25)  # Number of results to return
        
        # Perform vector search
        results = Vector_Search(query, k=k)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        print(f"Email search error: {str(e)}")
        return jsonify({'error': f'Failed to search emails: {str(e)}'}), 500

@app.route('/api/emails/status', methods=['GET'])
def email_status():
    """Get email loading status"""
    try:
        last_checked = get_last_checked_time()
        
        return jsonify({
            'last_checked': last_checked.isoformat() if last_checked else None,
            'status': 'ready'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get email status: {str(e)}'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status and configuration"""
    try:
        # Check if required files exist
        config_status = {
            'credentials_json': os.path.exists('credentials.json'),
            'token_json': os.path.exists('token.json'),
            'groq_api_key': bool(os.getenv('GROQ_API_KEY')),
            'vector_index': os.path.exists('index_email.index'),
            'email_metadata': os.path.exists('index_email_metadata.db')
        }
        
        return jsonify({
            'status': 'running',
            'config_status': config_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system status: {str(e)}'}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config = {
            'groq_api_key_set': bool(os.getenv('GROQ_API_KEY')),
            'gmail_credentials_exist': os.path.exists('credentials.json'),
            'gmail_token_exist': os.path.exists('token.json')
        }
        
        return jsonify({'config': config})
        
    except Exception as e:
        return jsonify({'error': f'Failed to get configuration: {str(e)}'}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuration data is required'}), 400
        
        # Handle API key updates
        if 'groq_api_key' in data:
            api_key = data['groq_api_key'].strip()
            if api_key:
                # Update environment variable (temporary for current session)
                os.environ['GROQ_API_KEY'] = api_key
                
                # Update .env file
                env_file = '.env'
                env_content = ''
                
                if os.path.exists(env_file):
                    with open(env_file, 'r') as f:
                        lines = f.readlines()
                    
                    # Update existing key or add new one
                    key_found = False
                    for i, line in enumerate(lines):
                        if line.startswith('GROQ_API_KEY='):
                            lines[i] = f'GROQ_API_KEY={api_key}\n'
                            key_found = True
                            break
                    
                    if not key_found:
                        lines.append(f'GROQ_API_KEY={api_key}\n')
                    
                    env_content = ''.join(lines)
                else:
                    env_content = f'GROQ_API_KEY={api_key}\n'
                
                with open(env_file, 'w') as f:
                    f.write(env_content)
        
        return jsonify({'message': 'Configuration updated successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to update configuration: {str(e)}'}), 500

# Web fallback routes
@app.route('/')
def index():
    """Serve the main HTML file for web access"""
    try:
        return send_file(frontend_dir / 'index.html')
    except:
        return "<h1>Gmail RAG Assistant</h1><p>Web interface not available. Please use the Electron app.</p>"

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    try:
        if filename == 'index.html':
            return send_file(frontend_dir / 'index.html')
        return send_from_directory(frontend_dir, filename)
    except Exception as e:
        return f"File not found: {filename}", 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def run_server():
    """Run the Flask server"""
    try:
        print("Starting Gmail RAG Assistant Backend Server...")
        print("Server running on http://localhost:5000")
        
        # Run Flask server
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Change to the correct working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    run_server()