import { useState, useEffect } from 'react'
import { Check, ChevronDown, ChevronUp, AlertCircle, Loader2, Sparkles, Clock } from 'lucide-react'
import { recommendDomains } from '../services/api'

function InterestSelector({ profile, onSelect }) {
  const [recommendations, setRecommendations] = useState([])
  const [selectedTools, setSelectedTools] = useState([])
  const [expandedDomains, setExpandedDomains] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (profile) {
      fetchRecommendations()
    }
  }, [profile])

  const fetchRecommendations = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await recommendDomains(profile)
      if (response.success) {
        setRecommendations(response.recommendations || [])
        // Auto-expand first domain
        if (response.recommendations && response.recommendations.length > 0) {
          setExpandedDomains({ [response.recommendations[0].domain]: true })
        }
      } else {
        throw new Error(response.message || 'Failed to fetch recommendations')
      }
    } catch (err) {
      let errorMessage = err.response?.data?.message || err.message || 'Failed to load recommendations'
      
      // Provide more helpful message for timeout errors
      if (err.message?.includes('timeout') || err.message?.includes('timed out')) {
        errorMessage = 'The AI recommendation is taking longer than expected. This can happen with complex profiles. Please try again - it may work on the second attempt.'
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const toggleDomain = (domainName) => {
    setExpandedDomains(prev => ({
      ...prev,
      [domainName]: !prev[domainName]
    }))
  }

  const toggleTool = (tool) => {
    setSelectedTools(prev => {
      const toolId = `${tool.name}-${tool.domain || ''}`
      const exists = prev.find(t => `${t.name}-${t.domain || ''}` === toolId)
      if (exists) {
        return prev.filter(t => `${t.name}-${t.domain || ''}` !== toolId)
      } else {
        if (prev.length >= 8) {
          return prev // Max 8 tools
        }
        return [...prev, { ...tool, domain: tool.domain || 'unknown' }]
      }
    })
  }

  const isToolSelected = (tool) => {
    const toolId = `${tool.name}-${tool.domain || ''}`
    return selectedTools.some(t => `${t.name}-${t.domain || ''}` === toolId)
  }

  const getTotalLearningTime = () => {
    return selectedTools.reduce((total, tool) => {
      return total + (tool.learning_time_weeks || 0)
    }, 0)
  }

  const handleGenerate = () => {
    if (selectedTools.length >= 2 && onSelect) {
      onSelect(selectedTools)
    }
  }

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'Easy': 'bg-green-100 text-green-800 border-green-300',
      'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Challenging': 'bg-red-100 text-red-800 border-red-300',
    }
    return colors[difficulty] || colors.Moderate
  }

  const getMarketDemandColor = (demand) => {
    const colors = {
      'High': 'bg-blue-100 text-blue-800 border-blue-300',
      'Medium': 'bg-gray-100 text-gray-800 border-gray-300',
    }
    return colors[demand] || colors.Medium
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-xl p-8 max-w-6xl mx-auto">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mb-4" />
          <p className="text-gray-600 text-lg">Loading AI recommendations...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-xl p-8 max-w-6xl mx-auto">
        <div className="text-center py-8">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 font-semibold mb-4">{error}</p>
          <button
            onClick={fetchRecommendations}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-xl shadow-xl p-8 mb-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-2">
            <Sparkles className="h-8 w-8 text-purple-600" />
            Select Your Learning Path
          </h2>
          <p className="text-gray-600">Choose tools and technologies to master</p>
        </div>

        {/* Selection Summary - Sticky */}
        <div className="sticky top-4 z-10 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6 border-2 border-blue-200 shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tools Selected</p>
              <p className="text-2xl font-bold text-gray-800">{selectedTools.length} / 8</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Estimated Time</p>
              <p className="text-2xl font-bold text-gray-800 flex items-center gap-1">
                <Clock className="h-5 w-5" />
                {getTotalLearningTime()} weeks
              </p>
            </div>
          </div>
          {selectedTools.length >= 8 && (
            <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-yellow-800 text-sm flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Maximum 8 tools selected. Remove some to add others.
            </div>
          )}
          {selectedTools.length < 2 && (
            <div className="mt-2 p-2 bg-blue-100 border border-blue-300 rounded text-blue-800 text-sm">
              Select at least 2 tools to continue
            </div>
          )}
        </div>

        {/* Domain Recommendations */}
        <div className="space-y-4">
          {recommendations.map((domain, index) => (
            <div
              key={index}
              className="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-400 transition-all"
            >
              {/* Domain Header */}
              <button
                onClick={() => toggleDomain(domain.domain)}
                className="w-full p-6 bg-gradient-to-r from-gray-50 to-blue-50 hover:from-blue-50 hover:to-indigo-50 transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-4 flex-1 text-left">
                  <div className="bg-purple-100 rounded-lg p-3">
                    <Sparkles className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-800">{domain.domain}</h3>
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">
                        Recommended for you
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{domain.reason}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getDifficultyColor(domain.difficulty)}`}>
                        {domain.difficulty}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getMarketDemandColor(domain.market_demand)}`}>
                        {domain.market_demand} Demand
                      </span>
                    </div>
                  </div>
                </div>
                {expandedDomains[domain.domain] ? (
                  <ChevronUp className="h-6 w-6 text-gray-600" />
                ) : (
                  <ChevronDown className="h-6 w-6 text-gray-600" />
                )}
              </button>

              {/* Domain Tools - Expandable */}
              {expandedDomains[domain.domain] && domain.key_tools && (
                <div className="p-6 bg-white border-t border-gray-200">
                  <p className="text-sm font-semibold text-gray-700 mb-4">Available Tools:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {domain.key_tools.map((tool, toolIndex) => {
                      const isSelected = isToolSelected({ ...tool, domain: domain.domain })
                      return (
                        <div
                          key={toolIndex}
                          onClick={() => toggleTool({ ...tool, domain: domain.domain })}
                          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                            isSelected
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-800 mb-1">{tool.name}</h4>
                              {tool.description && (
                                <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                              )}
                              {tool.learning_time_weeks && (
                                <div className="flex items-center gap-1 text-xs text-gray-500">
                                  <Clock className="h-3 w-3" />
                                  {tool.learning_time_weeks} weeks
                                </div>
                              )}
                            </div>
                            <div className={`ml-3 p-2 rounded ${isSelected ? 'bg-blue-500' : 'bg-gray-200'}`}>
                              {isSelected ? (
                                <Check className="h-4 w-4 text-white" />
                              ) : (
                                <div className="h-4 w-4" />
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Generate Button */}
        <div className="mt-8">
          <button
            onClick={handleGenerate}
            disabled={selectedTools.length < 2 || selectedTools.length > 8}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg"
          >
            <Sparkles className="h-5 w-5" />
            Generate My Roadmap ({selectedTools.length} tools selected)
          </button>
        </div>
      </div>
    </div>
  )
}

export default InterestSelector
