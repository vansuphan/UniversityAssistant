export interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  source?: 'faq' | 'openai' | 'function' | 'demo' | 'rag'
  confidence?: number
}

export interface QuickAction {
  icon: React.ComponentType<{ className?: string }>
  text: string
  action: string
}

