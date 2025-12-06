import { useState } from 'react'
import ResumeUpload from './components/ResumeUpload'
import InterestSelector from './components/InterestSelector'
import TimeCommitment from './components/TimeCommitment'
import RoadmapDisplay from './components/RoadmapDisplay'
import AIChat from './components/AIChat'
import { generateRoadmap } from './services/api'
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react'

function App() {
  const [step, setStep] = useState(1)
  const [resumeData, setResumeData] = useState(null)
  const [profile, setProfile] = useState(null)
  const [selectedTools, setSelectedTools] = useState([])
  const [preferences, setPreferences] = useState({})
  const [roadmap, setRoadmap] = useState(null)
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false)
  const [error, setError] = useState(null)

  const handleResumeComplete = (data) => {
    setResumeData(data.resumeText)
    setProfile(data.profile)
    setStep(2)
  }

  const handleToolsSelected = (tools) => {
    setSelectedTools(tools)
    setStep(3)
  }

  const handlePreferencesSet = async (prefs) => {
    setPreferences(prefs)
    setGeneratingRoadmap(true)
    setError(null)

    try {
      const userData = {
        profile: profile,
        selected_tools: selectedTools.map(tool => tool.name),
        hours_per_week: prefs.hoursPerWeek,
        learning_style: prefs.learningStyle || 'balanced',
        deadline: prefs.deadline || null,
      }

      const response = await generateRoadmap(userData)
      
      if (response.success) {
        setRoadmap(response.roadmap)
        setStep(4)
      } else {
        throw new Error(response.message || 'Failed to generate roadmap')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to generate roadmap. Please try again.')
    } finally {
      setGeneratingRoadmap(false)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
      setError(null)
    }
  }

  const handleStartOver = () => {
    setStep(1)
    setResumeData(null)
    setProfile(null)
    setSelectedTools([])
    setPreferences({})
    setRoadmap(null)
    setError(null)
  }

  const steps = [
    { number: 1, name: 'Upload Resume', icon: '📄' },
    { number: 2, name: 'Select Tools', icon: '🛠️' },
    { number: 3, name: 'Set Preferences', icon: '⚙️' },
    { number: 4, name: 'View Roadmap', icon: '🗺️' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">AI Career Roadmap Generator</h1>
              <p className="text-sm text-gray-600">Powered by OpenRouter AI</p>
            </div>
            {step > 1 && (
              <button
                onClick={handleStartOver}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Start Over
              </button>
            )}
          </div>

          {/* Step Indicator */}
          <div className="mt-4 flex items-center justify-between">
            {steps.map((stepItem, index) => (
              <div key={stepItem.number} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                      step >= stepItem.number
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {step > stepItem.number ? (
                      <CheckCircle className="h-6 w-6" />
                    ) : (
                      <span>{stepItem.number}</span>
                    )}
                  </div>
                  <span className={`text-xs mt-2 font-medium ${
                    step >= stepItem.number ? 'text-gray-800' : 'text-gray-500'
                  }`}>
                    {stepItem.name}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 rounded ${
                      step > stepItem.number ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Error Display */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-800 font-semibold mb-1">Error</p>
              <p className="text-red-700 text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Loading State for Roadmap Generation */}
        {generatingRoadmap && (
          <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-xl p-12">
            <div className="text-center">
              <Loader2 className="h-16 w-16 text-blue-600 animate-spin mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Generating Your Roadmap</h3>
              <p className="text-gray-600 mb-6">This may take 10-20 seconds...</p>
              <div className="space-y-2 text-left max-w-md mx-auto">
                <div className="flex items-center gap-2 text-gray-700">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <span>Analyzing your goals...</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <span>Curating resources...</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <span>Generating timeline...</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <span>Finalizing roadmap...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step Content */}
        {!generatingRoadmap && (
          <>
            {step === 1 && (
              <ResumeUpload onComplete={handleResumeComplete} />
            )}

            {step === 2 && profile && (
              <div className="space-y-4">
                <InterestSelector
                  profile={profile}
                  onSelect={handleToolsSelected}
                />
                <div className="max-w-6xl mx-auto">
                  <button
                    onClick={handleBack}
                    className="px-6 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    ← Back
                  </button>
                </div>
              </div>
            )}

            {step === 3 && selectedTools.length > 0 && (
              <div className="space-y-4">
                <TimeCommitment
                  selectedTools={selectedTools}
                  onSelect={handlePreferencesSet}
                />
                <div className="max-w-4xl mx-auto">
                  <button
                    onClick={handleBack}
                    className="px-6 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    ← Back
                  </button>
                </div>
              </div>
            )}

            {step === 4 && roadmap && (
              <div className="space-y-6">
                <RoadmapDisplay roadmap={roadmap} profile={profile} />
                <div className="max-w-7xl mx-auto">
                  <button
                    onClick={handleStartOver}
                    className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Generate New Roadmap
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* AI Chat - Available after step 2 */}
      {step >= 2 && <AIChat roadmap={roadmap} profile={profile} />}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>© 2024 AI Career Roadmap Generator | Powered by OpenRouter AI</p>
        </div>
      </footer>
    </div>
  )
}

export default App
