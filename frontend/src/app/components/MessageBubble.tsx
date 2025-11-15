'use client'

import { Bot, User, Database, Zap, MessageSquare, Search } from 'lucide-react'
import { Message } from '../types'
import MarkdownBlock from './MarkdownBlock'

interface MessageBubbleProps {
  message: Message
}

const getSourceIcon = (source?: string) => {
  switch (source) {
    case 'faq':
      return <span title='FAQ'><Database className="w-3 h-3 text-green-500" /></span>
    case 'rag':
      return <span title='RAG (Retrieval-Augmented Generation)'><Search className="w-3 h-3 text-orange-500" /></span>
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
    case 'rag':
      return 'RAG'
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

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex items-start space-x-2 max-w-[80%] ${
          isUser ? 'flex-row-reverse space-x-reverse' : ''
        }`}
      >
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-600'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4" />
          ) : (
            <Bot className="w-4 h-4" />
          )}
        </div>
        <div className="flex flex-col space-y-1 max-w-full">
          <div
            className={`px-4 py-2 rounded-2xl ${
              isUser
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <p className="whitespace-pre-wrap">
              {message.content}
              {/* <MarkdownBlock
                markdown={message.content}
              /> */}
            </p>
            <div className="flex items-center justify-between mt-2">
              <p
                className={`text-xs ${
                  isUser ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString('vi-VN', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              
              {!isUser && (
                <div className="flex items-center space-x-2">
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
        </div>
      </div>
    </div>
  )
}

