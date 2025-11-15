'use client'

import { Bot, FolderOpen } from 'lucide-react'

interface HeaderProps {
  onOpenKnowledgeBase: () => void
}

export default function Header({ onOpenKnowledgeBase }: HeaderProps) {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-full">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Student Support Chatbot</h1>
            <p className="text-blue-100 text-sm">Trợ lý ảo với AI thông minh</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenKnowledgeBase}
            className="flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium transition-colors bg-white/20 hover:bg-white/30 text-blue-100"
            title="Quản lý Knowledge Base"
          >
            <FolderOpen className="w-4 h-4" />
            <span>Knowledge Base</span>
          </button>
        </div>
      </div>
    </div>
  )
}

