'use client'

import { QUICK_ACTIONS } from '../constants'

interface QuickActionsProps {
  onActionClick: (action: string) => void
}

export default function QuickActions({ onActionClick }: QuickActionsProps) {
  return (
    <div className="bg-gray-50 p-4 border-b">
      <p className="text-sm text-gray-600 mb-2">Hành động nhanh:</p>
      <div className="flex flex-wrap gap-2">
        {QUICK_ACTIONS.map((action, index) => {
          const Icon = action.icon
          return (
            <button
              key={index}
              onClick={() => onActionClick(action.action)}
              className="flex items-center space-x-2 bg-white hover:bg-blue-50 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-full border border-gray-200 hover:border-blue-300 transition-colors text-sm"
            >
              <Icon className="w-4 h-4" />
              <span>{action.text}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

