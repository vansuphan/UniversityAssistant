'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, BookOpen, Calendar, DollarSign, HelpCircle, Volume2, VolumeX, Loader, Zap, Database, MessageSquare } from 'lucide-react'
import axios from 'axios'

interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  audio?: string
  source?: 'faq' | 'openai' | 'function' | 'demo'
  confidence?: number
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Xin chào! Tôi là trợ lý ảo nâng cao của trường đại học với khả năng tìm kiếm thông minh và chuyển đổi giọng nói! 🎙️ Tôi có thể giúp bạn với thông tin về môn học, lịch thi, học phí và các dịch vụ sinh viên. Bạn cần hỗ trợ gì? 😊',
      sender: 'bot',
      timestamp: new Date(),
      source: 'demo'
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const [audioEnabled, setAudioEnabled] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const playAudio = (audioBase64: string, messageId: string) => {
    try {
      if (isPlaying) {
        // Stop current playing audio
        setIsPlaying(false)
        setPlayingMessageId(null)
        return
      }

      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`)
      setIsPlaying(true)
      setPlayingMessageId(messageId)
      
      audio.play()
      
      audio.onended = () => {
        setIsPlaying(false)
        setPlayingMessageId(null)
      }
      
      audio.onerror = () => {
        console.error('Audio playback failed')
        setIsPlaying(false)
        setPlayingMessageId(null)
      }
    } catch (error) {
      console.error('Audio playback error:', error)
      setIsPlaying(false)
      setPlayingMessageId(null)
    }
  }

  const getSourceIcon = (source?: string) => {
    switch (source) {
      case 'faq':
        return <span title='FAQ'><Database className="w-3 h-3 text-green-500" /></span>
      case 'function':
        return <span title='Function Call'><Zap className="w-3 h-3 text-blue-500" /></span>
      case 'openai':
        return <span title='AI Response'><MessageSquare className="w-3 h-3 text-purple-500" /></span>
      default:
        return <span title='System'><Bot className="w-3 h-3 text-gray-500" /></span>
    }
  }

  const getSourceLabel = (source?: string, confidence?: number) => {
    switch (source) {
      case 'faq':
        return `FAQ ${confidence ? `(${(confidence * 100).toFixed(0)}%)` : ''}`
      case 'function':
        return 'Function'
      case 'openai':
        return 'AI'
      case 'demo':
        return 'Demo'
      default:
        return 'System'
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post('http://localhost:5001/api/chat', {
        message: inputMessage,
        session_id: sessionId,
        include_audio: audioEnabled
      })

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        audio: response.data.audio,
        source: response.data.source,
        confidence: response.data.confidence
      }

      setMessages(prev => [...prev, botMessage])
      
      // Auto-play audio if enabled and available
      if (audioEnabled && response.data.audio && !isPlaying) {
        setTimeout(() => {
          playAudio(response.data.audio, botMessage.id)
        }, 500) // Small delay to ensure UI is updated
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.',
        sender: 'bot',
        timestamp: new Date(),
        source: undefined as 'faq' | 'openai' | 'function' | 'demo' | undefined
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickActions = [
    {
      icon: BookOpen,
      text: 'Thông tin môn học',
      action: 'Cho tôi biết thông tin về môn CS101'
    },
    {
      icon: Calendar,
      text: 'Lịch thi',
      action: 'Khi nào thi cuối kỳ môn Data Structures?'
    },
    {
      icon: DollarSign,
      text: 'Tính học phí',
      action: 'Tính học phí cho 15 tín chỉ đại học'
    },
    {
      icon: HelpCircle,
      text: 'Dịch vụ sinh viên',
      action: 'Tôi cần tư vấn dịch vụ thư viện'
    }
  ]

  const handleQuickAction = (action: string) => {
    setInputMessage(action)
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-full">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Student Support Chatbot</h1>
              <p className="text-blue-100 text-sm">Trợ lý ảo với AI thông minh + TTS</p>
            </div>
          </div>
          
          {/* Audio Controls */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-blue-100">Âm thanh:</span>
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  audioEnabled 
                    ? 'bg-green-500 hover:bg-green-600 text-white' 
                    : 'bg-white/20 hover:bg-white/30 text-blue-100'
                }`}
                title={audioEnabled ? 'Tắt âm thanh' : 'Bật âm thanh'}
              >
                {audioEnabled ? (
                  <>
                    <Volume2 className="w-4 h-4" />
                    <span>Bật</span>
                  </>
                ) : (
                  <>
                    <VolumeX className="w-4 h-4" />
                    <span>Tắt</span>
                  </>
                )}
              </button>
            </div>
            
            {isPlaying && (
              <div className="flex items-center space-x-1 text-green-300">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-xs">Đang phát...</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-50 p-4 border-b">
        <p className="text-sm text-gray-600 mb-2">Hành động nhanh:</p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action.action)}
              className="flex items-center space-x-2 bg-white hover:bg-blue-50 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-full border border-gray-200 hover:border-blue-300 transition-colors text-sm"
            >
              <action.icon className="w-4 h-4" />
              <span>{action.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`flex items-start space-x-2 max-w-[80%] ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {message.sender === 'user' ? (
                  <User className="w-4 h-4" />
                ) : (
                  <Bot className="w-4 h-4" />
                )}
              </div>
              <div className="flex flex-col space-y-1 max-w-full">
                <div
                  className={`px-4 py-2 rounded-2xl ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Message metadata */}
                  <div className="flex items-center justify-between mt-2">
                    <p
                      className={`text-xs ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString('vi-VN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                    
                    {/* Audio button and source info for bot messages */}
                    {message.sender === 'bot' && (
                      <div className="flex items-center space-x-2">
                        {/* Audio button */}
                        {message.audio && (
                          <button
                            onClick={() => playAudio(message.audio!, message.id)}
                            disabled={isPlaying && playingMessageId !== message.id}
                            className={`p-1 rounded-full transition-colors ${
                              playingMessageId === message.id && isPlaying
                                ? 'bg-green-200 text-green-700'
                                : 'bg-gray-200 hover:bg-gray-300 text-gray-600'
                            }`}
                            title={playingMessageId === message.id && isPlaying ? 'Đang phát âm thanh' : 'Phát âm thanh'}
                          >
                            {playingMessageId === message.id && isPlaying ? (
                              <Loader className="w-3 h-3 animate-spin" />
                            ) : (
                              <Volume2 className="w-3 h-3" />
                            )}
                          </button>
                        )}
                        
                        {/* Source indicator */}
                        <div className="flex items-center space-x-1 text-xs">
                          {getSourceIcon(message.source)}
                          <span className="text-gray-500">
                            {getSourceLabel(message.source, message.confidence)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* FAQ confidence indicator */}
                {message.source === 'faq' && message.confidence && (
                  <div className="flex items-center space-x-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full self-start">
                    <Database className="w-3 h-3" />
                    <span>Tìm thấy trong FAQ - Độ chính xác {(message.confidence * 100).toFixed(0)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-2 rounded-full transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Nhấn Enter để gửi, Shift+Enter để xuống dòng
        </p>
      </div>
    </div>
  )
}
