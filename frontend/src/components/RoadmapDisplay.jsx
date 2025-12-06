import { useState } from 'react'
import { CheckCircle, Circle, ChevronDown, ChevronRight, Calendar, Clock, BookOpen, Code, Target, Download, Copy, Share2, ExternalLink, AlertCircle } from 'lucide-react'

function RoadmapDisplay({ roadmap, profile }) {
  const [expandedPhases, setExpandedPhases] = useState({})
  const [selectedWeek, setSelectedWeek] = useState(1)
  const [expandedProjects, setExpandedProjects] = useState({})
  const [resourceFilters, setResourceFilters] = useState({
    tool: 'all',
    type: 'all',
    difficulty: 'all',
    free: 'all',
  })

  if (!roadmap) {
    return (
      <div className="bg-white rounded-xl shadow-xl p-12 text-center">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-48 mx-auto"></div>
        </div>
      </div>
    )
  }

  const togglePhase = (phaseIndex) => {
    setExpandedPhases(prev => ({
      ...prev,
      [phaseIndex]: !prev[phaseIndex]
    }))
  }

  const toggleProject = (projectIndex) => {
    setExpandedProjects(prev => ({
      ...prev,
      [projectIndex]: !prev[projectIndex]
    }))
  }

  const filteredResources = roadmap.resources?.filter(resource => {
    if (resourceFilters.tool !== 'all' && !resource.title.toLowerCase().includes(resourceFilters.tool.toLowerCase())) return false
    if (resourceFilters.type !== 'all' && resource.type !== resourceFilters.type) return false
    if (resourceFilters.difficulty !== 'all' && resource.difficulty !== resourceFilters.difficulty) return false
    if (resourceFilters.free !== 'all') {
      const isFree = resource.is_free === true || resource.is_free === 'true'
      if (resourceFilters.free === 'free' && !isFree) return false
      if (resourceFilters.free === 'paid' && isFree) return false
    }
    return true
  }) || []

  const handleExportPDF = () => {
    window.print()
  }

  const handleCopyMarkdown = async () => {
    let markdown = `# Career Roadmap\n\n`
    markdown += `**Duration:** ${roadmap.total_duration_weeks} weeks\n`
    markdown += `**Completion Date:** ${roadmap.estimated_completion_date}\n\n`
    
    roadmap.phases?.forEach((phase, i) => {
      markdown += `## Phase ${i + 1}: ${phase.title}\n\n`
      markdown += `**Duration:** ${phase.duration_weeks} weeks\n\n`
      phase.milestones?.forEach(milestone => {
        markdown += `### ${milestone.name}\n\n`
        milestone.tasks?.forEach(task => {
          markdown += `- [ ] ${task}\n`
        })
        markdown += `\n`
      })
    })
    
    try {
      await navigator.clipboard.writeText(markdown)
      alert('Roadmap copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Overview Card */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-xl p-8 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold mb-2">Your Career Roadmap</h2>
            <p className="text-blue-100">Personalized learning path powered by AI</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleExportPDF}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg flex items-center gap-2 transition-all"
            >
              <Download className="h-4 w-4" />
              Export PDF
            </button>
            <button
              onClick={handleCopyMarkdown}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg flex items-center gap-2 transition-all"
            >
              <Copy className="h-4 w-4" />
              Copy
            </button>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="h-5 w-5" />
              <p className="text-sm text-blue-100">Duration</p>
            </div>
            <p className="text-2xl font-bold">{roadmap.total_duration_weeks} weeks</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-5 w-5" />
              <p className="text-sm text-blue-100">Completion</p>
            </div>
            <p className="text-lg font-bold">{roadmap.estimated_completion_date || 'TBD'}</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <Code className="h-5 w-5" />
              <p className="text-sm text-blue-100">Phases</p>
            </div>
            <p className="text-2xl font-bold">{roadmap.phases?.length || 0}</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="h-5 w-5" />
              <p className="text-sm text-blue-100">Resources</p>
            </div>
            <p className="text-2xl font-bold">{roadmap.resources?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Phase Timeline */}
      <div className="bg-white rounded-xl shadow-xl p-8">
        <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <Target className="h-6 w-6 text-blue-600" />
          Learning Phases
        </h3>
        <div className="space-y-4">
          {roadmap.phases?.map((phase, phaseIndex) => (
            <div key={phaseIndex} className="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-400 transition-all">
              <button
                onClick={() => togglePhase(phaseIndex)}
                className="w-full p-6 bg-gradient-to-r from-gray-50 to-blue-50 hover:from-blue-50 hover:to-indigo-50 transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-4 flex-1 text-left">
                  <div className="bg-blue-100 rounded-lg p-3">
                    <span className="text-2xl font-bold text-blue-600">P{phaseIndex + 1}</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-gray-800 mb-1">{phase.title}</h4>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {phase.duration_weeks} weeks
                      </span>
                      <span className="flex items-center gap-1">
                        <Code className="h-4 w-4" />
                        {phase.tools_covered?.length || 0} tools
                      </span>
                    </div>
                  </div>
                </div>
                {expandedPhases[phaseIndex] ? (
                  <ChevronDown className="h-6 w-6 text-gray-600" />
                ) : (
                  <ChevronRight className="h-6 w-6 text-gray-600" />
                )}
              </button>

              {expandedPhases[phaseIndex] && (
                <div className="p-6 bg-white border-t border-gray-200">
                  <div className="mb-4">
                    <h5 className="font-semibold text-gray-700 mb-2">Learning Objectives</h5>
                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                      {phase.learning_objectives?.map((obj, i) => (
                        <li key={i}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-4">
                    <h5 className="font-semibold text-gray-700 mb-2">Milestones</h5>
                    <div className="space-y-3">
                      {phase.milestones?.map((milestone, mIndex) => (
                        <div key={mIndex} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                          <div className="flex items-center gap-2 mb-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            <h6 className="font-semibold text-gray-800">{milestone.name}</h6>
                          </div>
                          {milestone.tasks && (
                            <ul className="ml-7 space-y-1">
                              {milestone.tasks.map((task, tIndex) => (
                                <li key={tIndex} className="text-sm text-gray-600 flex items-center gap-2">
                                  <Circle className="h-3 w-3" />
                                  {task}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  {phase.tools_covered && phase.tools_covered.length > 0 && (
                    <div>
                      <h5 className="font-semibold text-gray-700 mb-2">Tools Covered</h5>
                      <div className="flex flex-wrap gap-2">
                        {phase.tools_covered.map((tool, tIndex) => (
                          <span key={tIndex} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Schedule */}
      {roadmap.weekly_schedule && roadmap.weekly_schedule.length > 0 && (
        <div className="bg-white rounded-xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Calendar className="h-6 w-6 text-blue-600" />
            Weekly Schedule
          </h3>
          <div className="flex gap-2 mb-6 overflow-x-auto">
            {roadmap.weekly_schedule.slice(0, 4).map((week, index) => (
              <button
                key={index}
                onClick={() => setSelectedWeek(index + 1)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                  selectedWeek === index + 1
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Week {week.week_number || index + 1}
              </button>
            ))}
          </div>
          {roadmap.weekly_schedule[selectedWeek - 1] && (
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <h4 className="text-xl font-bold text-gray-800 mb-4">
                Week {roadmap.weekly_schedule[selectedWeek - 1].week_number || selectedWeek}: {roadmap.weekly_schedule[selectedWeek - 1].primary_focus}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {roadmap.weekly_schedule[selectedWeek - 1].daily_tasks && (
                  <div>
                    <h5 className="font-semibold text-gray-700 mb-2">Daily Tasks</h5>
                    <ul className="space-y-1">
                      {roadmap.weekly_schedule[selectedWeek - 1].daily_tasks.map((task, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                          <Circle className="h-3 w-3 mt-1.5 flex-shrink-0" />
                          {task}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {roadmap.weekly_schedule[selectedWeek - 1].practice_exercises && (
                  <div>
                    <h5 className="font-semibold text-gray-700 mb-2">Practice Exercises</h5>
                    <ul className="space-y-1">
                      {roadmap.weekly_schedule[selectedWeek - 1].practice_exercises.map((exercise, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                          <Circle className="h-3 w-3 mt-1.5 flex-shrink-0" />
                          {exercise}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              {roadmap.weekly_schedule[selectedWeek - 1].time_allocation && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <strong>Time Allocation:</strong> {roadmap.weekly_schedule[selectedWeek - 1].time_allocation}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Resources Library */}
      {roadmap.resources && roadmap.resources.length > 0 && (
        <div className="bg-white rounded-xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-blue-600" />
            Learning Resources
          </h3>
          
          {/* Filters */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <select
              value={resourceFilters.type}
              onChange={(e) => setResourceFilters({ ...resourceFilters, type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Types</option>
              <option value="Course">Course</option>
              <option value="Video">Video</option>
              <option value="Article">Article</option>
              <option value="Documentation">Documentation</option>
              <option value="Book">Book</option>
            </select>
            <select
              value={resourceFilters.difficulty}
              onChange={(e) => setResourceFilters({ ...resourceFilters, difficulty: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Difficulties</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
            <select
              value={resourceFilters.free}
              onChange={(e) => setResourceFilters({ ...resourceFilters, free: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Resources</option>
              <option value="free">Free Only</option>
              <option value="paid">Paid Only</option>
            </select>
            <button
              onClick={() => setResourceFilters({ tool: 'all', type: 'all', difficulty: 'all', free: 'all' })}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Clear Filters
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredResources.map((resource, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-all">
                <div className="flex items-start justify-between mb-2">
                  <h5 className="font-semibold text-gray-800 flex-1">{resource.title}</h5>
                  {resource.is_free && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                      Free
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                  <span className="px-2 py-1 bg-gray-100 rounded text-xs">{resource.type}</span>
                  <span className="px-2 py-1 bg-gray-100 rounded text-xs">{resource.platform}</span>
                  {resource.difficulty && (
                    <span className={`px-2 py-1 rounded text-xs ${
                      resource.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                      resource.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {resource.difficulty}
                    </span>
                  )}
                </div>
                {resource.estimated_time && (
                  <p className="text-sm text-gray-600 mb-2 flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {resource.estimated_time}
                  </p>
                )}
                {resource.why_this_resource && (
                  <p className="text-xs text-gray-500 mb-3">{resource.why_this_resource}</p>
                )}
                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Open Resource <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Project Ideas */}
      {roadmap.projects && roadmap.projects.length > 0 && (
        <div className="bg-white rounded-xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Code className="h-6 w-6 text-blue-600" />
            Project Ideas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {roadmap.projects.map((project, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-xl p-6 hover:border-blue-400 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <h4 className="text-xl font-bold text-gray-800">{project.title}</h4>
                  <button
                    onClick={() => toggleProject(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {expandedProjects[index] ? (
                      <ChevronDown className="h-5 w-5" />
                    ) : (
                      <ChevronRight className="h-5 w-5" />
                    )}
                  </button>
                </div>
                <p className="text-gray-600 mb-4">{project.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.technologies?.map((tech, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                      {tech}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                  <span className={`px-2 py-1 rounded ${
                    project.complexity === 'Beginner' ? 'bg-green-100 text-green-800' :
                    project.complexity === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {project.complexity}
                  </span>
                  {project.estimated_time && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {project.estimated_time}
                    </span>
                  )}
                </div>
                {expandedProjects[index] && (
                  <div className="mt-4 space-y-3">
                    {project.learning_outcomes && (
                      <div>
                        <h5 className="font-semibold text-gray-700 mb-2">Learning Outcomes</h5>
                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                          {project.learning_outcomes.map((outcome, i) => (
                            <li key={i}>{outcome}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {project.steps && (
                      <div>
                        <h5 className="font-semibold text-gray-700 mb-2">Step-by-Step Guide</h5>
                        <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                          {project.steps.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Career Insights */}
      {roadmap.career_insights && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl shadow-xl p-8 border-2 border-purple-200">
          <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Target className="h-6 w-6 text-purple-600" />
            Career Insights
          </h3>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{roadmap.career_insights}</p>
        </div>
      )}

      {/* Skill Gap Analysis */}
      {roadmap.skill_gap_analysis && (
        <div className="bg-white rounded-xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <AlertCircle className="h-6 w-6 text-blue-600" />
            Skill Gap Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {roadmap.skill_gap_analysis.strengths && roadmap.skill_gap_analysis.strengths.length > 0 && (
              <div>
                <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Your Strengths
                </h4>
                <ul className="space-y-2">
                  {roadmap.skill_gap_analysis.strengths.map((strength, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {roadmap.skill_gap_analysis.gaps && roadmap.skill_gap_analysis.gaps.length > 0 && (
              <div>
                <h4 className="font-semibold text-orange-700 mb-3 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Skills to Develop
                </h4>
                <ul className="space-y-2">
                  {roadmap.skill_gap_analysis.gaps.map((gap, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <Circle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          {roadmap.skill_gap_analysis.strategies && roadmap.skill_gap_analysis.strategies.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-blue-700 mb-3">Strategies</h4>
              <ul className="space-y-2">
                {roadmap.skill_gap_analysis.strategies.map((strategy, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    {strategy}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default RoadmapDisplay
