import { BookOpen, Calendar, DollarSign, HelpCircle } from 'lucide-react'
import { QuickAction } from '../types'

export const QUICK_ACTIONS: QuickAction[] = [
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

export const API_BASE_URL = 'http://localhost:5001'

export const INITIAL_MESSAGE = {
  id: '1',
  content: 'Xin chào! Tôi là trợ lý ảo nâng cao của trường đại học với khả năng tìm kiếm thông minh và chuyển đổi giọng nói! 🎙️ Tôi có thể giúp bạn với thông tin về môn học, lịch thi, học phí và các dịch vụ sinh viên. Bạn cần hỗ trợ gì? 😊',
  sender: 'bot' as const,
  timestamp: new Date(),
  source: 'demo' as const
}

