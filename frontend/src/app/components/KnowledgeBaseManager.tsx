'use client'

import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, Trash2, X, Plus, Loader, CheckCircle, AlertCircle, File, FolderOpen } from 'lucide-react'
import axios from 'axios'

interface Document {
  title: string
  category: string
  created_at: string
  chunks: number
}

interface KnowledgeBaseManagerProps {
  isOpen: boolean
  onClose: () => void
}

const API_BASE_URL = 'http://localhost:5001'

export default function KnowledgeBaseManager({ isOpen, onClose }: KnowledgeBaseManagerProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadMode, setUploadMode] = useState<'file' | 'text'>('file')
  const [showUploadForm, setShowUploadForm] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null)

  // Form states
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('general')
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Load documents on mount and when modal opens
  useEffect(() => {
    if (isOpen) {
      loadDocuments()
    }
  }, [isOpen])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/api/knowledge/documents`)
      if (response.data.success) {
        setDocuments(response.data.documents || [])
      }
    } catch (error) {
      console.error('Error loading documents:', error)
      setMessage({ type: 'error', text: 'Không thể tải danh sách documents' })
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (selectedFile: File) => {
    if (!allowedFile(selectedFile.name)) {
      setMessage({ type: 'error', text: 'File type không được hỗ trợ. Chỉ chấp nhận PDF, DOCX, TXT' })
      return
    }
    setFile(selectedFile)
    if (!title) {
      setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''))
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const allowedFile = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    return ['pdf', 'docx', 'doc', 'txt'].includes(ext || '')
  }

  const handleUploadFile = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Vui lòng chọn file' })
      return
    }

    setUploading(true)
    setMessage(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title || file.name)
      formData.append('category', category)

      const response = await axios.post(`${API_BASE_URL}/api/knowledge/upload-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        setMessage({ type: 'success', text: `Upload thành công! Đã tạo ${response.data.chunks_count} chunks` })
        resetForm()
        loadDocuments()
        setTimeout(() => {
          setShowUploadForm(false)
          setMessage(null)
        }, 2000)
      }
    } catch (error: any) {
      console.error('Error uploading file:', error)
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Có lỗi xảy ra khi upload file' 
      })
    } finally {
      setUploading(false)
    }
  }

  const handleUploadText = async () => {
    if (!title.trim() || !content.trim()) {
      setMessage({ type: 'error', text: 'Vui lòng điền đầy đủ tiêu đề và nội dung' })
      return
    }

    setUploading(true)
    setMessage(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/knowledge/upload-text`, {
        title: title.trim(),
        content: content.trim(),
        category: category
      })

      if (response.data.success) {
        setMessage({ type: 'success', text: `Thêm text thành công! Đã tạo ${response.data.chunks_count} chunks` })
        resetForm()
        loadDocuments()
        setTimeout(() => {
          setShowUploadForm(false)
          setMessage(null)
        }, 2000)
      }
    } catch (error: any) {
      console.error('Error uploading text:', error)
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Có lỗi xảy ra khi thêm text' 
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docTitle: string) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa document "${docTitle}"?`)) {
      return
    }

    setDeleteLoading(docTitle)
    try {
      const encodedTitle = encodeURIComponent(docTitle)
      const response = await axios.delete(`${API_BASE_URL}/api/knowledge/documents/${encodedTitle}`)
      
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Xóa document thành công' })
        loadDocuments()
        setTimeout(() => setMessage(null), 2000)
      }
    } catch (error: any) {
      console.error('Error deleting document:', error)
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Có lỗi xảy ra khi xóa document' 
      })
    } finally {
      setDeleteLoading(null)
    }
  }

  const resetForm = () => {
    setFile(null)
    setTitle('')
    setContent('')
    setCategory('general')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClose = () => {
    resetForm()
    setShowUploadForm(false)
    setMessage(null)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-t-lg flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FolderOpen className="w-6 h-6" />
            <h2 className="text-xl font-bold">Quản lý Knowledge Base</h2>
          </div>
          <button
            onClick={handleClose}
            className="text-white hover:bg-white/20 p-2 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Message */}
          {message && (
            <div
              className={`mb-4 p-3 rounded-lg flex items-center space-x-2 ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {message.type === 'success' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span>{message.text}</span>
            </div>
          )}

          {/* Upload Button */}
          {!showUploadForm && (
            <div className="mb-6">
              <button
                onClick={() => setShowUploadForm(true)}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Plus className="w-5 h-5" />
                <span>Thêm Document</span>
              </button>
            </div>
          )}

          {/* Upload Form */}
          {showUploadForm && (
            <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Thêm Document</h3>
                <button
                  onClick={() => {
                    setShowUploadForm(false)
                    resetForm()
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Mode Toggle */}
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => setUploadMode('file')}
                  className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                    uploadMode === 'file'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <File className="w-4 h-4 inline mr-2" />
                  Upload File
                </button>
                <button
                  onClick={() => setUploadMode('text')}
                  className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                    uploadMode === 'text'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <FileText className="w-4 h-4 inline mr-2" />
                  Nhập Text
                </button>
              </div>

              {/* File Upload Mode */}
              {uploadMode === 'file' && (
                <div className="space-y-4">
                  {/* Drag & Drop Area */}
                  <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      dragActive
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 bg-white hover:border-gray-400'
                    }`}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileInputChange}
                      accept=".pdf,.docx,.doc,.txt"
                      className="hidden"
                    />
                    <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-600 mb-2">
                      Kéo thả file vào đây hoặc{' '}
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="text-blue-600 hover:underline"
                      >
                        chọn file
                      </button>
                    </p>
                    <p className="text-sm text-gray-500">
                      Hỗ trợ: PDF, DOCX, TXT (tối đa 10MB)
                    </p>
                    {file && (
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <File className="w-5 h-5 text-blue-600" />
                          <span className="text-sm font-medium">{file.name}</span>
                          <span className="text-xs text-gray-500">
                            ({(file.size / 1024).toFixed(2)} KB)
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            setFile(null)
                            if (fileInputRef.current) fileInputRef.current.value = ''
                          }}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Title and Category */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tiêu đề
                      </label>
                      <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Nhập tiêu đề..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Danh mục
                      </label>
                      <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="general">General</option>
                        <option value="courses">Courses</option>
                        <option value="exams">Exams</option>
                        <option value="regulations">Regulations</option>
                        <option value="services">Services</option>
                        <option value="tuition">Tuition</option>
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={handleUploadFile}
                    disabled={!file || uploading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                  >
                    {uploading ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        <span>Đang upload...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        <span>Upload File</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Text Input Mode */}
              {uploadMode === 'text' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tiêu đề
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Nhập tiêu đề..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nội dung
                    </label>
                    <textarea
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Nhập nội dung document..."
                      rows={8}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Danh mục
                    </label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="general">General</option>
                      <option value="courses">Courses</option>
                      <option value="exams">Exams</option>
                      <option value="regulations">Regulations</option>
                      <option value="services">Services</option>
                      <option value="tuition">Tuition</option>
                    </select>
                  </div>
                  <button
                    onClick={handleUploadText}
                    disabled={!title.trim() || !content.trim() || uploading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                  >
                    {uploading ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        <span>Đang thêm...</span>
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5" />
                        <span>Thêm Text</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Documents List */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Documents ({documents.length})</h3>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FolderOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>Chưa có documents nào. Hãy thêm document đầu tiên!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <h4 className="font-semibold text-gray-800">{doc.title}</h4>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center space-x-1">
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                              {doc.category}
                            </span>
                          </span>
                          <span>{doc.chunks} chunks</span>
                          <span>
                            {new Date(doc.created_at).toLocaleDateString('vi-VN', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(doc.title)}
                        disabled={deleteLoading === doc.title}
                        className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        title="Xóa document"
                      >
                        {deleteLoading === doc.title ? (
                          <Loader className="w-5 h-5 animate-spin" />
                        ) : (
                          <Trash2 className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50 rounded-b-lg flex justify-end">
          <button
            onClick={handleClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  )
}

