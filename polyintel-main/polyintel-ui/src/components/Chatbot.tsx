import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, X, Minimize2, Maximize2 } from 'lucide-react';
import APIService from '../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  audioUrl?: string;
  timestamp: Date;
}

interface ChatbotProps {
  context?: {
    selectedMarket?: any;
    analysis?: any;
  };
}

export default function Chatbot({ context }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your PolyIntel assistant. I can help you understand markets, analyze sentiment, and answer questions about prediction markets. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text: string, useVoice: boolean = false) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chatbot/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: text,
          context: context,
          use_voice: true, // Always request voice response (uses Hathora TTS)
        }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        audioUrl: data.audio_url,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input, false);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob) => {
    setIsLoading(true);

    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/chatbot/voice-input`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            audio_data: base64Audio,
            context: context,
          }),
        });

        if (!response.ok) throw new Error('Failed to process voice');

        const data = await response.json();

        const userMessage: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: `[Voice: ${data.response ? 'Question sent' : 'Processing...'}]`,
          timestamp: new Date(),
        };

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          audioUrl: data.audio_url,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage, assistantMessage]);
        setIsLoading(false);
      };

      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Voice message error:', error);
      setIsLoading(false);
    }
  };

  const playAudio = (audioUrl: string, messageId: string) => {
    if (isPlayingAudio === messageId) {
      // Stop playing
      setIsPlayingAudio(null);
      return;
    }

    setIsPlayingAudio(messageId);
    const audio = new Audio(audioUrl);
    audio.onended = () => setIsPlayingAudio(null);
    audio.onerror = () => {
      setIsPlayingAudio(null);
      alert('Could not play audio');
    };
    audio.play();
  };

  if (isMinimized) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-4 right-4 bg-cyan-600 hover:bg-cyan-700 text-white p-4 rounded-full shadow-lg z-50 flex items-center gap-2 transition-all hover:scale-105"
        title="Open chat"
        aria-label="Open chat"
      >
        <Maximize2 size={20} />
        <span className="font-medium">Chat</span>
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-gray-800 border border-gray-700 rounded-lg shadow-2xl flex flex-col z-50">
      {/* Header */}
      <div className="bg-cyan-600 px-4 py-3 rounded-t-lg flex items-center justify-between">
        <h3 className="text-white font-semibold">PolyIntel Assistant</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(true)}
            className="text-white hover:bg-cyan-700 p-2 rounded transition-colors"
            title="Minimize chat"
            aria-label="Minimize chat"
          >
            <Minimize2 size={18} />
          </button>
          <button
            onClick={() => setMessages([messages[0]])}
            className="text-white hover:bg-cyan-700 p-2 rounded transition-colors"
            title="Clear chat"
            aria-label="Clear chat"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-100'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.audioUrl && message.role === 'assistant' && (
                <button
                  onClick={() => playAudio(message.audioUrl!, message.id)}
                  className="mt-2 flex items-center gap-1 text-xs text-cyan-300 hover:text-cyan-200"
                >
                  <Volume2 size={14} />
                  {isPlayingAudio === message.id ? 'Playing...' : 'Play Audio'}
                </button>
              )}
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about markets..."
            className="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            disabled={isLoading || isRecording}
          />
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-2 rounded-lg ${
              isRecording
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
            disabled={isLoading}
          >
            {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            type="submit"
            className="bg-cyan-600 hover:bg-cyan-700 text-white p-2 rounded-lg"
            disabled={isLoading || isRecording || !input.trim()}
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

