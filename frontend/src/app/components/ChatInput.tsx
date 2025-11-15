'use client'

import { Send } from 'lucide-react'

interface ChatInputProps {
  inputMessage: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onSend: () => void
}

export default function ChatInput({ inputMessage, isLoading, onInputChange, onSend }: ChatInputProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="border-t bg-white p-4">
      <div className="flex space-x-2">
        <textarea
          id="chat-input"
          value={inputMessage}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Nhập câu hỏi của bạn..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isLoading}
          rows={1}
        />
        <button
          onClick={onSend}
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
  )
}

