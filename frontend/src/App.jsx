import { useState, useEffect, React } from 'react'
import ResumeUpload from './components/ResumeUpload'
import InterestSelector from './components/InterestSelector'
import TimeCommitment from './components/TimeCommitment'
import RoadmapDisplay from './components/RoadmapDisplay'
import RoadmapList from './components/RoadmapList'
import RoadmapDetail from './components/RoadmapDetail'
import DebugRoadmapData from './components/DebugRoadmapData'
import AIChat from './components/AIChat'
import { generateRoadmap } from './services/api'
import { saveRoadmap } from './services/roadmapservice'
import { Loader2, CheckCircle, AlertCircle, BookOpen, LogOut, User } from 'lucide-react'
import { onAuthStateChanged, signOut } from "firebase/auth"
import { auth } from "./firebase"
import Signup from "./Signup"
import Login from "./Login"


function App() {
  const [step, setStep] = useState(1)
  const [resumeData, setResumeData] = useState(null)
  const [profile, setProfile] = useState(null)
  const [selectedTools, setSelectedTools] = useState([])
  const [preferences, setPreferences] = useState({})
  const [roadmap, setRoadmap] = useState(null)
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false)
  const [error, setError] = useState(null)
  const [user, setUser] = useState(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [savingRoadmap, setSavingRoadmap] = useState(false)
  const [currentRoadmapId, setCurrentRoadmapId] = useState(null)

  // New state for navigation between views
  const [view, setView] = useState('generator') // 'generator', 'list', 'detail'
  const [selectedRoadmapId, setSelectedRoadmapId] = useState(null)

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setAuthChecked(true);
    });

    return () => unsub();
  }, []);

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

  const handleSaveRoadmap = async () => {
    if (!user) {
      setError('Please login to save your roadmap')
      return
    }

    if (!roadmap) {
      setError('No roadmap to save')
      return
    }

    setSavingRoadmap(true)
    setError(null)

    try {
      console.log('=== DEBUG: Saving Roadmap ===')
      console.log('Profile:', profile)
      console.log('Selected Tools:', selectedTools)
      console.log('Preferences:', preferences)
      console.log('Roadmap:', roadmap)

      // Extract learning resources from phases if they exist
      let learningResources = [];
      if (roadmap.phases && Array.isArray(roadmap.phases)) {
        learningResources = roadmap.phases.map(phase => ({
          toolName: phase.title || 'Unknown',
          phase_number: phase.phase_number,
          duration_weeks: phase.duration_weeks,
          learning_objectives: phase.learning_objectives || [],
          milestones: phase.milestones || [],
          tools_covered: phase.tools_covered || [],
          resources: [] // You can map phase resources here if they exist
        }));
      } else if (roadmap.learning_resources) {
        learningResources = roadmap.learning_resources;
      } else if (roadmap.learningResources) {
        learningResources = roadmap.learningResources;
      }

      // Structure the roadmap data for Firebase
      const roadmapToSave = {
        profileAnalysis: {
          experienceLevel: profile?.experience_level || 'Junior',
          yearsOfExperience: profile?.years_of_experience || 0,
          technicalSkills: Array.isArray(profile?.technical_skills) ? profile.technical_skills : [],
          topStrengths: Array.isArray(profile?.top_strengths) ? profile.top_strengths : [],
          domainExpertise: Array.isArray(profile?.domain_expertise) ? profile.domain_expertise : []
        },
        selectedTools: Array.isArray(selectedTools) ? selectedTools.map(tool => ({
          name: tool?.name || tool?.tool_name || 'Unknown Tool',
          category: tool?.domain || tool?.category || 'General',
          difficulty: tool?.difficulty || 'Moderate',
          estimatedTime: tool?.learning_time_weeks ? `${tool.learning_time_weeks} weeks` : (tool?.estimated_time || tool?.estimatedTime || 'N/A'),
          description: tool?.description || ''
        })) : [],
        learningPreferences: {
          hoursPerWeek: preferences?.hoursPerWeek || 6,
          learningStyle: preferences?.learningStyle || 'balanced',
          deadline: preferences?.deadline || null,
          hasDeadline: !!preferences?.deadline,
          estimatedCompletion: preferences?.estimatedCompletion || roadmap?.estimated_completion_date || null,
          totalWeeks: preferences?.totalWeeks || roadmap?.estimated_weeks || 10
        },
        learningPlan: {
          totalTools: Array.isArray(selectedTools) ? selectedTools.length : 0,
          estimatedWeeks: roadmap?.estimated_weeks || roadmap?.estimatedWeeks || preferences?.totalWeeks || 10,
          hoursPerWeek: preferences?.hoursPerWeek || 6,
          completionDate: preferences?.deadline || preferences?.estimatedCompletion || roadmap?.estimated_completion_date || null
        },
        learningResources: learningResources,
        phases: roadmap?.phases || [],
        projectIdeas: Array.isArray(roadmap?.project_ideas)
          ? roadmap.project_ideas
          : Array.isArray(roadmap?.projectIdeas)
            ? roadmap.projectIdeas
            : [],
        careerInsights: roadmap?.career_insights || roadmap?.careerInsights || {},
        skillGaps: {
          yourStrengths: Array.isArray(profile?.technical_skills) ? profile.technical_skills : [],
          skillsToDevelop: Array.isArray(selectedTools) ? selectedTools.map(t => t?.name || t?.tool_name || 'Unknown') : []
        },
        progress: 0,
        completedTools: [],
        completedPhases: [],
        currentTool: Array.isArray(selectedTools) && selectedTools.length > 0
          ? (selectedTools[0]?.name || selectedTools[0]?.tool_name || null)
          : null
      }

      console.log('=== Structured Roadmap to Save ===')
      console.log(JSON.stringify(roadmapToSave, null, 2))

      const result = await saveRoadmap(user.uid, roadmapToSave)

      if (result.success) {
        setCurrentRoadmapId(result.roadmapId)
        alert('🎉 Roadmap saved successfully!')
        console.log('Roadmap saved with ID:', result.roadmapId)
      } else {
        throw new Error(result.error || 'Failed to save roadmap')
      }
    } catch (err) {
      console.error('Error saving roadmap:', err)
      setError(err.message || 'Failed to save roadmap. Please try again.')
    } finally {
      setSavingRoadmap(false)
    }
  }

  const handleViewMyRoadmaps = () => {
    setView('list')
  }

  const handleViewRoadmapDetail = (roadmapId) => {
    setSelectedRoadmapId(roadmapId)
    setView('detail')
  }

  const handleBackToGenerator = () => {
    setView('generator')
    setSelectedRoadmapId(null)
  }

  const handleBackToList = () => {
    setView('list')
    setSelectedRoadmapId(null)
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
    setCurrentRoadmapId(null)
  }

  // NEW: Logout handler
  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      try {
        await signOut(auth);
        // Reset all state
        setStep(1)
        setResumeData(null)
        setProfile(null)
        setSelectedTools([])
        setPreferences({})
        setRoadmap(null)
        setError(null)
        setCurrentRoadmapId(null)
        setView('generator')
        setSelectedRoadmapId(null)
        // User state will be automatically cleared by onAuthStateChanged
      } catch (error) {
        console.error('Error logging out:', error);
        setError('Failed to logout. Please try again.');
      }
    }
  }

  const steps = [
    { number: 1, name: 'Upload Resume', icon: '📄' },
    { number: 2, name: 'Select Tools', icon: '🛠️' },
    { number: 3, name: 'Set Preferences', icon: '⚙️' },
    { number: 4, name: 'View Roadmap', icon: '🗺️' },
  ]

  if (!authChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        {showSignup ? (
          <Signup onSwitch={() => setShowSignup(false)} />
        ) : (
          <Login onSwitch={() => setShowSignup(true)} />
        )}
      </div>
    )
  }

  // Render RoadmapList view
  if (view === 'list') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">My Learning Roadmaps</h1>
                <p className="text-sm text-gray-600">Manage and track your learning journey</p>
              </div>
              <div className="flex items-center gap-2">
                {/* User Email Display */}
                <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                  <User className="h-4 w-4 text-gray-600" />
                  <span className="text-sm text-gray-700">{user?.email}</span>
                </div>

                <button
                  onClick={handleBackToGenerator}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create New Roadmap
                </button>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            </div>
          </div>
        </header>
        <RoadmapList
          onViewDetail={handleViewRoadmapDetail}
          onBackToGenerator={handleBackToGenerator}
        />
      </div>
    )
  }

  // Render RoadmapDetail view
  if (view === 'detail' && selectedRoadmapId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Roadmap Details</h1>
                <p className="text-sm text-gray-600">Track your learning progress</p>
              </div>
              <div className="flex items-center gap-2">
                {/* User Email Display */}
                <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                  <User className="h-4 w-4 text-gray-600" />
                  <span className="text-sm text-gray-700">{user?.email}</span>
                </div>

                <button
                  onClick={handleBackToList}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  ← Back to List
                </button>
                <button
                  onClick={handleBackToGenerator}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create New
                </button>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            </div>
          </div>
        </header>
        <RoadmapDetail
          roadmapId={selectedRoadmapId}
          onBack={handleBackToList}
        />
      </div>
    )
  }

  // Render main generator view (default)
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
            <div className="flex items-center gap-2">
              {/* User Email Display */}
              <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                <User className="h-4 w-4 text-gray-600" />
                <span className="text-sm text-gray-700">{user?.email}</span>
              </div>

              <button
                onClick={handleViewMyRoadmaps}
                className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-2"
              >
                <BookOpen className="h-4 w-4" />
                My Roadmaps
              </button>
              {step > 1 && (
                <button
                  onClick={handleStartOver}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Start Over
                </button>
              )}

              {/* NEW: Logout Button */}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>

          {/* Step Indicator */}
          <div className="mt-4 flex items-center justify-between">
            {steps.map((stepItem, index) => (
              <div key={stepItem.number} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${step >= stepItem.number
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
                  <span className={`text-xs mt-2 font-medium ${step >= stepItem.number ? 'text-gray-800' : 'text-gray-500'
                    }`}>
                    {stepItem.name}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 rounded ${step > stepItem.number ? 'bg-blue-600' : 'bg-gray-200'
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
                <div className="max-w-7xl mx-auto flex gap-4">
                  <button
                    onClick={handleSaveRoadmap}
                    disabled={savingRoadmap || currentRoadmapId}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {savingRoadmap ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Saving...
                      </>
                    ) : currentRoadmapId ? (
                      <>
                        <CheckCircle className="h-5 w-5" />
                        Saved
                      </>
                    ) : (
                      <>
                        <BookOpen className="h-5 w-5" />
                        Save Roadmap
                      </>
                    )}
                  </button>

                  {currentRoadmapId && (
                    <button
                      onClick={handleViewMyRoadmaps}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      View My Roadmaps
                    </button>
                  )}

                  <button
                    onClick={handleStartOver}
                    className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
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

      {/* Debug Component - Remove in production */}
      {step === 4 && roadmap && (
        <DebugRoadmapData
          profile={profile}
          selectedTools={selectedTools}
          preferences={preferences}
          roadmap={roadmap}
        />
      )}

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