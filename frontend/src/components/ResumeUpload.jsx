import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle, X, Loader2, Sparkles } from 'lucide-react'
import { uploadResume, analyzeResume } from '../services/api'

function ResumeUpload({ onComplete }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [resumeText, setResumeText] = useState(null)
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
  const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
  const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']

  const validateFile = (file) => {
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
      throw new Error('Invalid file type. Please upload PDF, DOCX, or TXT file.')
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      throw new Error(`File size exceeds 5MB limit. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`)
    }

    return true
  }

  const handleFileSelect = (selectedFile) => {
    try {
      validateFile(selectedFile)
      setFile(selectedFile)
      setError(null)
      setUploadSuccess(false)
      setProfile(null)
    } catch (err) {
      setError(err.message)
      setFile(null)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      handleFileSelect(selectedFile)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const response = await uploadResume(file)
      if (response.success) {
        setUploadSuccess(true)
        setResumeText(response.data.raw_text)
        setFile({ ...file, uploaded: true })
      } else {
        throw new Error(response.message || 'Upload failed')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!resumeText) {
      setError('No resume text available for analysis')
      return
    }

    setAnalyzing(true)
    setError(null)

    try {
      const response = await analyzeResume(resumeText)
      if (response.success) {
        setProfile(response.profile)
      } else {
        throw new Error(response.message || 'Analysis failed')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Analysis failed. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleContinue = () => {
    if (profile && onComplete) {
      onComplete({
        resumeText,
        profile,
        file: file.name,
      })
    }
  }

  const getSkillCategory = (skill) => {
    const lowerSkill = skill.toLowerCase()
    if (lowerSkill.includes('python') || lowerSkill.includes('java') || lowerSkill.includes('javascript') || lowerSkill.includes('typescript') || lowerSkill.includes('go') || lowerSkill.includes('rust')) {
      return 'language'
    }
    if (lowerSkill.includes('react') || lowerSkill.includes('vue') || lowerSkill.includes('angular') || lowerSkill.includes('svelte')) {
      return 'framework'
    }
    if (lowerSkill.includes('aws') || lowerSkill.includes('azure') || lowerSkill.includes('gcp') || lowerSkill.includes('cloud')) {
      return 'cloud'
    }
    if (lowerSkill.includes('docker') || lowerSkill.includes('kubernetes') || lowerSkill.includes('ci/cd')) {
      return 'devops'
    }
    return 'other'
  }

  const getSkillColor = (category) => {
    const colors = {
      language: 'bg-blue-100 text-blue-800 border-blue-300',
      framework: 'bg-purple-100 text-purple-800 border-purple-300',
      cloud: 'bg-green-100 text-green-800 border-green-300',
      devops: 'bg-orange-100 text-orange-800 border-orange-300',
      other: 'bg-gray-100 text-gray-800 border-gray-300',
    }
    return colors[category] || colors.other
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="bg-white rounded-xl shadow-xl p-8 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Upload Your Resume</h2>
        <p className="text-gray-600">Get AI-powered career insights from your resume</p>
      </div>

      {/* Drag and Drop Zone */}
      {!uploadSuccess && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
            isDragging
              ? 'border-blue-500 bg-blue-50 scale-105'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <Upload className={`mx-auto h-16 w-16 mb-4 transition-colors ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} />
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="hidden"
            id="resume-upload"
          />
          <label
            htmlFor="resume-upload"
            className="cursor-pointer inline-block"
          >
            <span className="text-blue-600 hover:text-blue-700 font-semibold text-lg">
              Choose file
            </span>
            <span className="text-gray-600 mx-2">or drag and drop</span>
          </label>
          <p className="text-sm text-gray-500 mt-4">
            PDF, DOCX, or TXT (max 5MB)
          </p>
        </div>
      )}

      {/* File Preview */}
      {file && (
        <div className={`mt-6 p-4 rounded-lg border-2 ${
          uploadSuccess ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <p className="font-semibold text-gray-800">{file.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
              </div>
            </div>
            {uploadSuccess ? (
              <CheckCircle className="h-6 w-6 text-green-600" />
            ) : (
              <button
                onClick={() => {
                  setFile(null)
                  setError(null)
                  if (fileInputRef.current) fileInputRef.current.value = ''
                }}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-800">
            <X className="h-5 w-5" />
            <p className="font-medium">{error}</p>
          </div>
          {!uploadSuccess && (
            <button
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Dismiss
            </button>
          )}
        </div>
      )}

      {/* Upload Button */}
      {file && !uploadSuccess && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="mt-6 w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Uploading...
            </>
          ) : (
            'Upload Resume'
          )}
        </button>
      )}

      {/* Analyze Button */}
      {uploadSuccess && !profile && (
        <div className="mt-6">
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {analyzing ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>AI is analyzing your resume...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                <span>Analyze with AI</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Profile Display */}
      {profile && (
        <div className="mt-8 space-y-6 animate-fadeIn">
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
            <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-purple-600" />
              Your Profile Analysis
            </h3>

            {/* Experience Level & Years */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Experience Level</p>
                <p className="text-xl font-bold text-gray-800">{profile.experience_level || 'N/A'}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Years of Experience</p>
                <p className="text-xl font-bold text-gray-800">{profile.years_of_experience || 0} years</p>
              </div>
            </div>

            {/* Current Role */}
            {profile.current_role && (
              <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
                <p className="text-sm text-gray-600 mb-1">Current Role</p>
                <p className="text-lg font-semibold text-gray-800">{profile.current_role}</p>
              </div>
            )}

            {/* Skills */}
            {profile.skills && profile.skills.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-semibold text-gray-700 mb-3">Technical Skills</p>
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map((skill, index) => {
                    const category = getSkillCategory(skill)
                    return (
                      <span
                        key={index}
                        className={`px-3 py-1 rounded-full text-sm font-medium border ${getSkillColor(category)}`}
                      >
                        {skill}
                      </span>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Top Skills */}
            {profile.top_skills && profile.top_skills.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-semibold text-gray-700 mb-3">Top Strengths</p>
                <div className="flex flex-wrap gap-2">
                  {profile.top_skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800 border border-yellow-300"
                    >
                      ⭐ {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Domains */}
            {profile.domains && profile.domains.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-3">Domain Expertise</p>
                <div className="flex flex-wrap gap-2">
                  {profile.domains.map((domain, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 border border-indigo-300"
                    >
                      {domain}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center gap-2 shadow-lg"
          >
            <CheckCircle className="h-5 w-5" />
            Continue to Domain Selection
          </button>
        </div>
      )}
    </div>
  )
}

export default ResumeUpload
