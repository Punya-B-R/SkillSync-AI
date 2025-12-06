import { useState, useEffect } from 'react'
import { Clock, Calendar, AlertCircle, CheckCircle, Zap, Scale, Wind } from 'lucide-react'

function TimeCommitment({ selectedTools, onSelect }) {
  const [hoursPerWeek, setHoursPerWeek] = useState(6)
  const [learningStyle, setLearningStyle] = useState('balanced')
  const [deadline, setDeadline] = useState('')
  const [showDeadlinePicker, setShowDeadlinePicker] = useState(false)

  const totalWeeks = selectedTools?.reduce((sum, tool) => sum + (tool.learning_time_weeks || 0), 0) || 0
  const totalHours = totalWeeks * hoursPerWeek
  const estimatedMonths = Math.ceil(totalWeeks / 4)

  useEffect(() => {
    if (deadline) {
      calculateIntensity()
    }
  }, [deadline, hoursPerWeek, totalWeeks])

  const calculateIntensity = () => {
    if (!deadline || !totalWeeks) return null
    
    const deadlineDate = new Date(deadline)
    const today = new Date()
    const weeksUntilDeadline = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24 * 7))
    
    if (weeksUntilDeadline < totalWeeks) {
      return {
        level: 'unrealistic',
        message: 'Timeline is too ambitious. Consider extending your deadline or reducing tools.',
      }
    }
    
    const requiredHours = totalWeeks / weeksUntilDeadline * hoursPerWeek
    if (requiredHours > 20) {
      return {
        level: 'intensive',
        message: 'This will require intensive focus. Make sure you can commit this time.',
      }
    } else if (requiredHours > 10) {
      return {
        level: 'moderate',
        message: 'Moderate pace required. This is achievable with consistent effort.',
      }
    } else {
      return {
        level: 'comfortable',
        message: 'Comfortable pace. You have time for a balanced approach.',
      }
    }
  }

  const intensity = calculateIntensity()

  const getIntensityColor = (level) => {
    const colors = {
      unrealistic: 'bg-red-100 text-red-800 border-red-300',
      intensive: 'bg-orange-100 text-orange-800 border-orange-300',
      moderate: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      comfortable: 'bg-green-100 text-green-800 border-green-300',
    }
    return colors[level] || colors.moderate
  }

  const getCompletionDate = () => {
    if (deadline) {
      return new Date(deadline).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    }
    const completionDate = new Date()
    completionDate.setDate(completionDate.getDate() + (totalWeeks * 7))
    return completionDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  const handleContinue = () => {
    if (onSelect) {
      onSelect({
        hoursPerWeek,
        learningStyle,
        deadline: deadline || null,
        estimatedCompletion: getCompletionDate(),
        totalWeeks,
      })
    }
  }

  const getStyleIcon = (style) => {
    const icons = {
      fast: Zap,
      balanced: Scale,
      flexible: Wind,
    }
    return icons[style] || Scale
  }

  return (
    <div className="bg-white rounded-xl shadow-xl p-8 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Configure Your Learning</h2>
        <p className="text-gray-600">Set your pace and preferences</p>
      </div>

      {/* Hours Per Week Slider */}
      <div className="mb-8">
        <label className="block text-lg font-semibold text-gray-700 mb-4">
          <Clock className="inline h-5 w-5 mr-2" />
          Hours Per Week
        </label>
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl font-bold text-blue-600">{hoursPerWeek} hours</span>
            <div className="flex gap-2">
              {hoursPerWeek <= 5 && (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  Light
                </span>
              )}
              {hoursPerWeek > 5 && hoursPerWeek <= 10 && (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  Moderate
                </span>
              )}
              {hoursPerWeek > 10 && (
                <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                  Intensive
                </span>
              )}
            </div>
          </div>
          <input
            type="range"
            min="2"
            max="20"
            value={hoursPerWeek}
            onChange={(e) => setHoursPerWeek(Number(e.target.value))}
            className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-sm text-gray-500">
            <span>2 hrs</span>
            <span>11 hrs</span>
            <span>20 hrs</span>
          </div>
        </div>
      </div>

      {/* Learning Style */}
      <div className="mb-8">
        <label className="block text-lg font-semibold text-gray-700 mb-4">
          Learning Style
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { value: 'fast', label: 'Fast Track', desc: 'Learn quickly, intensive focus', icon: Zap },
            { value: 'balanced', label: 'Balanced', desc: 'Steady pace, sustainable learning', icon: Scale },
            { value: 'flexible', label: 'Flexible', desc: 'Learn at your own pace', icon: Wind },
          ].map((style) => {
            const Icon = style.icon
            return (
              <button
                key={style.value}
                onClick={() => setLearningStyle(style.value)}
                className={`p-6 rounded-xl border-2 transition-all text-left ${
                  learningStyle === style.value
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Icon className={`h-8 w-8 mb-3 ${learningStyle === style.value ? 'text-blue-600' : 'text-gray-400'}`} />
                <h3 className="font-bold text-gray-800 mb-1">{style.label}</h3>
                <p className="text-sm text-gray-600">{style.desc}</p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Deadline */}
      <div className="mb-8">
        <label className="block text-lg font-semibold text-gray-700 mb-4">
          <Calendar className="inline h-5 w-5 mr-2" />
          Deadline (Optional)
        </label>
        <div className="space-y-3">
          <div className="flex items-center gap-4">
            <input
              type="checkbox"
              checked={showDeadlinePicker}
              onChange={(e) => {
                setShowDeadlinePicker(e.target.checked)
                if (!e.target.checked) setDeadline('')
              }}
              className="h-5 w-5 text-blue-600 rounded"
            />
            <span className="text-gray-700">I have a specific deadline</span>
          </div>
          {showDeadlinePicker && (
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          )}
        </div>
      </div>

      {/* Summary Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200 mb-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Your Learning Plan Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Total Tools</p>
            <p className="text-2xl font-bold text-gray-800">{selectedTools?.length || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Estimated Weeks</p>
            <p className="text-2xl font-bold text-gray-800">{totalWeeks}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Hours Per Week</p>
            <p className="text-2xl font-bold text-gray-800">{hoursPerWeek}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Completion Date</p>
            <p className="text-lg font-bold text-gray-800">{getCompletionDate()}</p>
          </div>
        </div>

        {intensity && (
          <div className={`mt-4 p-4 rounded-lg border-2 ${getIntensityColor(intensity.level)}`}>
            <div className="flex items-start gap-2">
              {intensity.level === 'unrealistic' ? (
                <AlertCircle className="h-5 w-5 mt-0.5" />
              ) : (
                <CheckCircle className="h-5 w-5 mt-0.5" />
              )}
              <div>
                <p className="font-semibold mb-1">
                  {intensity.level === 'unrealistic' ? 'Timeline Warning' : 'Timeline Assessment'}
                </p>
                <p className="text-sm">{intensity.message}</p>
              </div>
            </div>
          </div>
        )}

        {!deadline && (
          <div className="mt-4 p-3 bg-white rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600">
              <strong>Estimated completion:</strong> {getCompletionDate()} ({estimatedMonths} months)
            </p>
          </div>
        )}
      </div>

      {/* Continue Button */}
      <button
        onClick={handleContinue}
        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center gap-2 shadow-lg"
      >
        <CheckCircle className="h-5 w-5" />
        Generate My Roadmap
      </button>
    </div>
  )
}

export default TimeCommitment
