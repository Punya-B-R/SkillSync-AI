import { useState } from 'react'
import { CheckCircle, Circle, ChevronDown, ChevronRight, Calendar, Clock, BookOpen, Code, Target, Download, Copy, Share2, ExternalLink, AlertCircle, Check, Dumbbell, BookOpen as BookOpenIcon } from 'lucide-react'

function RoadmapDisplay({ roadmap, profile }) {
  const [expandedPhases, setExpandedPhases] = useState({})
  const [expandedWeek, setExpandedWeek] = useState(null)
  const [expandedProjects, setExpandedProjects] = useState({})
  const [completedDays, setCompletedDays] = useState(new Set())

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

  const toggleWeek = (weekNumber) => {
    setExpandedWeek(expandedWeek === weekNumber ? null : weekNumber)
  }

  const toggleProject = (projectIndex) => {
    setExpandedProjects(prev => ({
      ...prev,
      [projectIndex]: !prev[projectIndex]
    }))
  }

  const toggleDayComplete = (weekNumber, dayNumber) => {
    const dayKey = `${weekNumber}-${dayNumber}`
    setCompletedDays(prev => {
      const newSet = new Set(prev)
      if (newSet.has(dayKey)) {
        newSet.delete(dayKey)
      } else {
        newSet.add(dayKey)
      }
      return newSet
    })
  }

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
              <Calendar className="h-5 w-5" />
              <p className="text-sm text-blue-100">Weeks</p>
            </div>
            <p className="text-2xl font-bold">{roadmap.weekly_plans?.length || roadmap.total_duration_weeks || 0}</p>
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
                        {phase.tools?.length || 0} tools
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
                      {phase.objectives?.map((obj, i) => (
                        <li key={i}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-4">
                    <h5 className="font-semibold text-gray-700 mb-2">Milestones</h5>
                    <div className="space-y-2">
                      {phase.milestones?.map((milestone, mIndex) => (
                        <div key={mIndex} className="bg-gray-50 rounded-lg p-3 border border-gray-200 flex items-start gap-2">
                          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-gray-700">{milestone}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  {phase.tools && phase.tools.length > 0 && (
                    <div>
                      <h5 className="font-semibold text-gray-700 mb-2">Tools Covered</h5>
                      <div className="flex flex-wrap gap-2">
                        {phase.tools.map((tool, tIndex) => (
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

      {/* Weekly Breakdown with Daily Plans */}
      {roadmap.weekly_plans && roadmap.weekly_plans.length > 0 && (
        <div className="bg-white rounded-xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Calendar className="h-6 w-6 text-blue-600" />
            Your Weekly Learning Plan
          </h3>
          <div className="space-y-6">
            {roadmap.weekly_plans.map((week) => {
              const isExpanded = expandedWeek === week.week
              const totalHours = week.daily_plans?.reduce((sum, day) => sum + (day.hours || 0), 0) || 0
              const completedCount = week.daily_plans?.filter(day => 
                completedDays.has(`${week.week}-${day.day}`)
              ).length || 0
              const completionPercentage = week.daily_plans ? Math.round((completedCount / week.daily_plans.length) * 100) : 0

              return (
                <div
                  key={week.week}
                  className="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-400 transition-all bg-white"
                >
                  {/* Week Header - Always visible */}
                  <button
                    onClick={() => toggleWeek(week.week)}
                    className="w-full p-6 flex justify-between items-center hover:bg-gray-50 transition-all text-left"
                    aria-expanded={isExpanded}
                    aria-label={`${isExpanded ? 'Collapse' : 'Expand'} week ${week.week}`}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-xl font-bold text-gray-800">
                          Week {week.week}: {week.focus}
                        </h4>
                        <span className="text-sm text-gray-500 flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {totalHours}h total
                        </span>
                      </div>
                      {week.objectives && week.objectives.length > 0 && (
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {week.objectives[0]}
                        </p>
                      )}
                    </div>
                    <ChevronDown
                      className={`h-6 w-6 text-gray-600 transition-transform duration-200 ${
                        isExpanded ? 'rotate-180' : ''
                      }`}
                    />
                  </button>

                  {/* Daily Plans - Expandable */}
                  {isExpanded && (
                    <div className="p-6 bg-gray-50 border-t border-gray-200 animate-in slide-in-from-top-2">
                      {/* Week Summary Stats */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-white rounded-lg border border-gray-200">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Total Hours</p>
                          <p className="text-lg font-bold text-gray-800">{totalHours}h</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Resources</p>
                          <p className="text-lg font-bold text-gray-800">{week.daily_plans?.length || 0}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Days Completed</p>
                          <p className="text-lg font-bold text-gray-800">{completedCount}/7</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Progress</p>
                          <p className="text-lg font-bold text-blue-600">{completionPercentage}%</p>
                        </div>
                      </div>

                      {/* Week Objectives */}
                      {week.objectives && week.objectives.length > 0 && (
                        <div className="mb-6">
                          <h5 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <Target className="h-5 w-5 text-blue-600" />
                            This week's objectives:
                          </h5>
                          <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600">
                            {week.objectives.map((obj, i) => (
                              <li key={i}>{obj}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Prerequisites */}
                      {week.prerequisites && week.prerequisites.length > 0 && (
                        <div className="mb-6 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                          <h5 className="font-semibold text-yellow-800 mb-2 text-sm">Prerequisites:</h5>
                          <ul className="list-disc pl-5 space-y-1 text-sm text-yellow-700">
                            {week.prerequisites.map((prereq, i) => (
                              <li key={i}>{prereq}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Daily Plans Grid */}
                      {week.daily_plans && week.daily_plans.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {week.daily_plans.map((day) => (
                            <DayCard
                              key={day.day}
                              day={day}
                              weekNumber={week.week}
                              isCompleted={completedDays.has(`${week.week}-${day.day}`)}
                              onToggleComplete={() => toggleDayComplete(week.week, day.day)}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
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
                    project.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                    project.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {project.difficulty || project.complexity}
                  </span>
                  {project.estimated_hours && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {project.estimated_hours}h
                    </span>
                  )}
                  {project.start_week && (
                    <span className="flex items-center gap-1 text-blue-600">
                      <Calendar className="h-4 w-4" />
                      Start Week {project.start_week}
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

// DayCard Component
function DayCard({ day, weekNumber, isCompleted, onToggleComplete }) {
  // Color coding based on day of week
  const getDayColor = (dayNum) => {
    if (dayNum <= 5) return 'blue' // Monday-Friday
    if (dayNum === 6) return 'purple' // Saturday
    return 'green' // Sunday
  }

  const dayColor = getDayColor(day.day)
  const colorClasses = {
    blue: 'border-blue-200 bg-gradient-to-br from-blue-50 to-white',
    purple: 'border-purple-200 bg-gradient-to-br from-purple-50 to-white',
    green: 'border-green-200 bg-gradient-to-br from-green-50 to-white'
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 border-2 transition-all duration-200 hover:shadow-lg ${
        colorClasses[dayColor]
      } ${isCompleted ? 'opacity-75' : ''}`}
    >
      {/* Day Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              dayColor === 'blue' ? 'bg-blue-100 text-blue-700' :
              dayColor === 'purple' ? 'bg-purple-100 text-purple-700' :
              'bg-green-100 text-green-700'
            }`}>
              DAY {day.day}
            </span>
            {isCompleted && (
              <CheckCircle className="h-5 w-5 text-green-600" />
            )}
          </div>
          <h4 className="font-bold text-lg text-gray-800">{day.topic}</h4>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="text-sm font-semibold text-gray-500">{day.hours}h</span>
          <button
            onClick={onToggleComplete}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            aria-label={isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {isCompleted ? '✓ Complete' : 'Mark done'}
          </button>
        </div>
      </div>

      {/* Tasks */}
      {day.tasks && day.tasks.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-semibold mb-2 text-gray-700 flex items-center gap-2">
            <Check className="h-4 w-4 text-green-500" />
            What you'll do:
          </p>
          <ul className="space-y-1.5">
            {day.tasks.map((task, i) => (
              <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                <CheckCircle className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
                <span className={isCompleted ? 'line-through text-gray-400' : ''}>{task}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Resource Section */}
      {day.resource && (
        <div className="bg-blue-50 rounded-md p-4 my-4 border-l-4 border-blue-500">
          <p className="text-sm font-semibold mb-2 text-gray-700 flex items-center gap-2">
            <BookOpenIcon className="h-4 w-4 text-blue-600" />
            Learning Resource:
          </p>
          <div className="space-y-2">
            <div className="flex gap-2 flex-wrap">
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded font-medium">
                {day.resource.type || 'Resource'}
              </span>
              {day.resource.platform && (
                <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                  {day.resource.platform}
                </span>
              )}
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded font-medium">
                ✓ FREE
              </span>
            </div>
            {day.resource.title && (
              <p className="font-medium text-gray-800">{day.resource.title}</p>
            )}
            {day.resource.what_to_learn && (
              <p className="text-sm text-gray-600">{day.resource.what_to_learn}</p>
            )}
            {day.resource.duration && (
              <p className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {day.resource.duration}
              </p>
            )}
            {day.resource.url && (
              <a
                href={day.resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium mt-2"
              >
                Access Resource
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            {!day.resource.url && (
              <div className="text-xs text-yellow-700 bg-yellow-50 p-2 rounded mt-2">
                ⚠️ Resource URL not available. Please search manually for: {day.resource.title}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Practice Section */}
      {day.practice && (
        <div className="bg-purple-50 rounded-md p-4 my-4 border-l-4 border-purple-500">
          <p className="text-sm font-semibold mb-1 text-gray-700 flex items-center gap-2">
            <Dumbbell className="h-4 w-4 text-purple-600" />
            Practice:
          </p>
          <p className="text-sm text-gray-700">{day.practice}</p>
        </div>
      )}

      {/* Outcome Section */}
      {day.outcome && (
        <div className="bg-green-50 rounded-md p-4 my-4 border-l-4 border-green-500">
          <p className="text-sm font-semibold mb-1 text-gray-700 flex items-center gap-2">
            <Target className="h-4 w-4 text-green-600" />
            By end of day:
          </p>
          <p className="text-sm text-gray-700">{day.outcome}</p>
        </div>
      )}
    </div>
  )
}

export default RoadmapDisplay
