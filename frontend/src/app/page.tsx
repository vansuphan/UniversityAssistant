'use client'

import { useState } from 'react'
import Header from './components/Header'
import QuickActions from './components/QuickActions'
import MessageList from './components/MessageList'
import ChatInput from './components/ChatInput'
import KnowledgeBaseManager from './components/KnowledgeBaseManager'
import { useChat } from './hooks/useChat'

export default function Home() {
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false)
  
  const { messages, inputMessage, isLoading, messagesEndRef, setInputMessage, sendMessage } = useChat()

  const handleSendMessage = () => {
    sendMessage()
  }

  const handleQuickAction = (action: string) => {
    setInputMessage(action)
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white shadow-2xl">
      <Header
        onOpenKnowledgeBase={() => setShowKnowledgeBase(true)}
      />

      <QuickActions onActionClick={handleQuickAction} />

      <MessageList
        messages={messages}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
      />

      <ChatInput
        inputMessage={inputMessage}
        isLoading={isLoading}
        onInputChange={setInputMessage}
        onSend={handleSendMessage}
      />

      <KnowledgeBaseManager
        isOpen={showKnowledgeBase}
        onClose={() => setShowKnowledgeBase(false)}
      />
    </div>
  )
}
