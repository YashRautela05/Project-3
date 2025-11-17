import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X, Bot, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your Crime-AI assistant. I can help you with crime analysis, safety recommendations, and emergency procedures. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponse = generateBotResponse(inputValue);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const generateBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('crime') || input.includes('robbery') || input.includes('theft')) {
      return "🚨 If you witness a crime in progress:\n\n1. **DO NOT** approach or confront anyone\n2. Call 911 immediately\n3. Provide detailed description of location and individuals\n4. Document license plates if visible\n5. Stay at a safe distance\n6. Take photos/videos if safe to do so\n\nYour safety comes first!";
    }
    
    if (input.includes('safety') || input.includes('protect')) {
      return "🛡️ **Personal Safety Tips:**\n\n• Always be aware of your surroundings\n• Trust your instincts\n• Keep emergency contacts handy\n• Avoid isolated areas at night\n• Share your location with trusted contacts\n• Learn basic self-defense techniques\n\nStay safe and alert!";
    }
    
    if (input.includes('emergency') || input.includes('help')) {
      return "🚨 **Emergency Contacts:**\n\n• **Police:** 911\n• **Crime Stoppers:** 1-800-222-TIPS\n• **National Emergency:** 911\n\n**If you're in immediate danger:**\n1. Call 911\n2. Find a safe location\n3. Stay on the line with dispatcher\n4. Follow their instructions\n\nHelp is always available!";
    }
    
    if (input.includes('analysis') || input.includes('detect')) {
      return "🔍 **Crime Detection Analysis:**\n\nOur AI system analyzes:\n• **Audio:** Speech patterns and distress signals\n• **Visual:** Object detection and suspicious behavior\n• **Context:** Location and time-based patterns\n• **Behavior:** Unusual movements and interactions\n\nUpload a video for real-time analysis!";
    }
    
    if (input.includes('hello') || input.includes('hi')) {
      return "👋 Hello! I'm here to help with crime detection and safety. You can ask me about:\n\n• Crime prevention tips\n• Emergency procedures\n• Safety recommendations\n• Analysis of suspicious activity\n\nWhat would you like to know?";
    }
    
    return "I'm here to help with crime detection and safety. You can ask me about crime prevention, emergency procedures, safety tips, or how our AI analysis works. What would you like to know?";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Chatbot Toggle Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-lg transition-all duration-200 hover:scale-110"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </motion.button>

      {/* Chatbot Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-24 right-6 z-40 w-96 h-96 bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col"
          >
            {/* Header */}
            <div className="bg-primary-600 text-white p-4 rounded-t-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <span className="font-semibold">Crime-AI Assistant</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.sender === 'bot' && <Bot className="h-4 w-4 mt-1 flex-shrink-0" />}
                      <div className="whitespace-pre-wrap text-sm">{message.text}</div>
                      {message.sender === 'user' && <User className="h-4 w-4 mt-1 flex-shrink-0" />}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-4 w-4" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about crime detection, safety tips..."
                  className="flex-1 input-field text-sm"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Chatbot;