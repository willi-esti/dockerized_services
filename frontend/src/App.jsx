import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, AlertCircle, CheckCircle } from 'lucide-react';
import { kronosApi } from './services/api';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check Ollama status on mount
    checkOllamaStatus();
  }, []);

  const checkOllamaStatus = async () => {
    try {
      const status = await kronosApi.getOllamaStatus();
      setOllamaStatus(status);
    } catch (error) {
      console.error('Failed to check Ollama status:', error);
      setOllamaStatus({ available: false, models: [] });
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await kronosApi.sendMessage(inputMessage);
      
      const aiMessage = {
        id: Date.now() + 1,
        text: response.reply,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        relevantMemory: response.relevant_memory,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">Kronos Chat</h1>
          <div className="flex items-center space-x-2">
            {ollamaStatus?.available ? (
              <div className="flex items-center text-green-600">
                <CheckCircle size={16} className="mr-1" />
                <span className="text-sm">AI Online</span>
              </div>
            ) : (
              <div className="flex items-center text-red-600">
                <AlertCircle size={16} className="mr-1" />
                <span className="text-sm">AI Offline</span>
              </div>
            )}
          </div>
        </div>
        {ollamaStatus?.models?.length > 0 && (
          <p className="text-sm text-gray-600 mt-1">
            Models: {ollamaStatus.models.join(', ')}
          </p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Bot size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-lg">Welcome to Kronos Chat!</p>
            <p className="text-sm">Ask me anything about your data and knowledge base.</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`flex max-w-xs lg:max-w-md xl:max-w-lg ${
                message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div
                className={`flex-shrink-0 ${
                  message.sender === 'user' ? 'ml-2' : 'mr-2'
                }`}
              >
                {message.sender === 'user' ? (
                  <User size={32} className="bg-blue-500 text-white p-1 rounded-full" />
                ) : (
                  <Bot size={32} className={`p-1 rounded-full ${
                    message.isError ? 'bg-red-500 text-white' : 'bg-gray-500 text-white'
                  }`} />
                )}
              </div>
              <div>
                <div
                  className={`px-4 py-2 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.isError
                      ? 'bg-red-100 text-red-800'
                      : 'bg-white text-gray-800 shadow'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                </div>
                <p className={`text-xs text-gray-500 mt-1 ${
                  message.sender === 'user' ? 'text-right' : 'text-left'
                }`}>
                  {message.timestamp}
                </p>
                {message.relevantMemory && message.relevantMemory.length > 0 && (
                  <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                    <p className="font-semibold text-blue-800">Relevant context found:</p>
                    {message.relevantMemory.slice(0, 2).map((memory, idx) => (
                      <p key={idx} className="text-blue-700 truncate">
                        • {memory.content.substring(0, 100)}...
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex flex-row">
              <Bot size={32} className="bg-gray-500 text-white p-1 rounded-full mr-2" />
              <div className="bg-white text-gray-800 shadow px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows="1"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
