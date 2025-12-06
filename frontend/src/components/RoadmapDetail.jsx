// components/RoadmapDetail.jsx
import React, { useState, useEffect } from 'react';
import { getRoadmapById, updateRoadmapProgress } from '../services/roadmapservice';
import { Loader2, AlertCircle } from 'lucide-react';

const RoadmapDetail = ({ roadmapId, onBack }) => {
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [completedItems, setCompletedItems] = useState(new Set());
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        fetchRoadmapDetail();
    }, [roadmapId]);

    const fetchRoadmapDetail = async () => {
        setLoading(true);
        setError(null);
        const result = await getRoadmapById(roadmapId);

        if (result.success) {
            setRoadmap(result.roadmap);
            if (result.roadmap.completedTools) {
                setCompletedItems(new Set(result.roadmap.completedTools));
            }
        } else {
            setError('Failed to load roadmap');
        }
        setLoading(false);
    };

    const handleToggleComplete = async (toolName) => {
        setUpdating(true);
        const newCompleted = new Set(completedItems);

        if (newCompleted.has(toolName)) {
            newCompleted.delete(toolName);
        } else {
            newCompleted.add(toolName);
        }

        const completedArray = Array.from(newCompleted);
        const progress = Math.round((completedArray.length / roadmap.selectedTools.length) * 100);

        const result = await updateRoadmapProgress(roadmapId, {
            completedTools: completedArray,
            progress: progress,
            currentTool: completedArray.length < roadmap.selectedTools.length
                ? roadmap.selectedTools[completedArray.length]?.name
                : null
        });

        if (result.success) {
            setCompletedItems(newCompleted);
            setRoadmap({
                ...roadmap,
                completedTools: completedArray,
                progress: progress
            });
        } else {
            setError('Failed to update progress');
        }
        setUpdating(false);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading roadmap details...</p>
                </div>
            </div>
        );
    }

    if (error && !roadmap) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 flex items-start gap-3">
                    <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                    <div>
                        <p className="text-red-800 font-semibold mb-1">Error</p>
                        <p className="text-red-700">{error}</p>
                        <button
                            onClick={onBack}
                            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                            Go Back
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!roadmap) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600">Roadmap not found</p>
                <button
                    onClick={onBack}
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    Go Back
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Error Banner */}
            {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
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

            {/* Overall Progress */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">Overall Progress</h2>
                        <p className="text-sm text-gray-600 mt-1">
                            {roadmap.profileAnalysis?.topStrengths?.join(' • ') || 'Your Learning Journey'}
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600">{roadmap.progress || 0}%</div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${roadmap.status === 'active' ? 'bg-green-100 text-green-800' :
                            roadmap.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                'bg-gray-100 text-gray-800'
                            }`}>
                            {roadmap.status}
                        </span>
                    </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                    <div
                        className="bg-blue-600 h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                        style={{ width: `${roadmap.progress || 0}%` }}
                    >
                        {roadmap.progress > 5 && (
                            <span className="text-xs text-white font-semibold">{roadmap.progress}%</span>
                        )}
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-gray-600 block mb-1">Completed</span>
                        <span className="text-lg font-semibold text-gray-900">
                            {completedItems.size} / {roadmap.selectedTools?.length || 0}
                        </span>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-gray-600 block mb-1">Duration</span>
                        <span className="text-lg font-semibold text-gray-900">
                            {roadmap.learningPlan?.estimatedWeeks || 'N/A'} weeks
                        </span>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-gray-600 block mb-1">Hours/Week</span>
                        <span className="text-lg font-semibold text-gray-900">
                            {roadmap.learningPreferences?.hoursPerWeek || 'N/A'} hrs
                        </span>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-gray-600 block mb-1">Learning Style</span>
                        <span className="text-lg font-semibold text-gray-900 capitalize">
                            {roadmap.learningPreferences?.learningStyle || 'Balanced'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Learning Tools */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    Learning Path
                    {updating && <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />}
                </h2>

                {/* If roadmap has phases, show phases structure */}
                {roadmap.phases && roadmap.phases.length > 0 ? (
                    <div className="space-y-6">
                        {roadmap.phases.map((phase, phaseIndex) => (
                            <div key={phaseIndex} className="border-2 border-gray-200 rounded-lg p-5">
                                <div className="mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                        Phase {phase.phase_number}: {phase.title}
                                    </h3>
                                    <div className="flex flex-wrap gap-2 mb-3">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                            {phase.duration_weeks} weeks
                                        </span>
                                        {phase.tools_covered?.map((tool, idx) => (
                                            <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {tool}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Learning Objectives */}
                                {phase.learning_objectives && phase.learning_objectives.length > 0 && (
                                    <div className="mb-4">
                                        <h4 className="font-medium text-gray-900 text-sm mb-2">Learning Objectives:</h4>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                            {phase.learning_objectives.map((objective, idx) => (
                                                <li key={idx}>{objective}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {/* Milestones */}
                                {phase.milestones && phase.milestones.length > 0 && (
                                    <div>
                                        <h4 className="font-medium text-gray-900 text-sm mb-2">Milestones:</h4>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                            {phase.milestones.map((milestone, idx) => (
                                                <li key={idx}>{milestone}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    /* Otherwise show tools structure */
                    <div className="space-y-4">
                        {roadmap.selectedTools?.map((tool, index) => {
                            const isCompleted = completedItems.has(tool.name);
                            const resources = roadmap.learningResources?.find(lr => lr.toolName === tool.name);

                            return (
                                <div
                                    key={index}
                                    className={`border-2 rounded-lg p-5 transition-all ${isCompleted
                                        ? 'bg-green-50 border-green-300'
                                        : 'bg-white border-gray-200 hover:border-blue-300'
                                        }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start space-x-4 flex-1">
                                            <input
                                                type="checkbox"
                                                checked={isCompleted}
                                                onChange={() => handleToggleComplete(tool.name)}
                                                disabled={updating}
                                                className="mt-1.5 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer disabled:opacity-50"
                                            />
                                            <div className="flex-1">
                                                <h3 className={`text-lg font-semibold mb-2 ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900'
                                                    }`}>
                                                    {index + 1}. {tool.name}
                                                </h3>
                                                {tool.description && (
                                                    <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                                                )}
                                                <div className="flex flex-wrap gap-2 mb-3">
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                        {tool.category}
                                                    </span>
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${tool.difficulty === 'High' || tool.difficulty === 'Challenging' ? 'bg-red-100 text-red-800' :
                                                        tool.difficulty === 'Moderate' || tool.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-green-100 text-green-800'
                                                        }`}>
                                                        {tool.difficulty}
                                                    </span>
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                                        {tool.estimatedTime}
                                                    </span>
                                                </div>

                                                {/* Learning Resources */}
                                                {resources && resources.resources && resources.resources.length > 0 && (
                                                    <div className="mt-4 space-y-2">
                                                        <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                                                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                                            </svg>
                                                            Learning Resources
                                                        </h4>
                                                        <div className="grid gap-2">
                                                            {resources.resources.slice(0, 3).map((resource, idx) => (
                                                                <a
                                                                    key={idx}
                                                                    href={resource.url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200"
                                                                >
                                                                    <div className="flex items-start justify-between gap-2">
                                                                        <div className="flex-1">
                                                                            <p className="text-sm font-medium text-gray-900 mb-1">{resource.title}</p>
                                                                            <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                                                                                <span className="inline-flex items-center">
                                                                                    {resource.type}
                                                                                </span>
                                                                                <span>•</span>
                                                                                <span>{resource.difficulty}</span>
                                                                                <span>•</span>
                                                                                <span>{resource.duration}</span>
                                                                            </div>
                                                                        </div>
                                                                        <svg className="h-5 w-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                                        </svg>
                                                                    </div>
                                                                </a>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Project Ideas */}
            {roadmap.projectIdeas && roadmap.projectIdeas.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                        <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                        Project Ideas
                    </h2>
                    <div className="grid gap-4 md:grid-cols-2">
                        {roadmap.projectIdeas.map((project, index) => (
                            <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                                <h3 className="font-semibold text-gray-900 mb-2">{project.title}</h3>
                                <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                                <div className="flex flex-wrap gap-2 mb-3">
                                    {project.technologies?.map((tech, idx) => (
                                        <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                            {tech}
                                        </span>
                                    ))}
                                </div>
                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                    <span className="inline-flex items-center gap-1">
                                        <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                        </svg>
                                        {project.difficulty}
                                    </span>
                                    <span className="inline-flex items-center gap-1">
                                        <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        {project.estimatedTime}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Skill Gap Analysis */}
            {roadmap.skillGaps && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                        <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        Skill Gap Analysis
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div>
                            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                                <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Your Strengths
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {roadmap.skillGaps.yourStrengths?.slice(0, 15).map((skill, idx) => (
                                    <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 font-medium">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold text-orange-900 mb-3 flex items-center gap-2">
                                <svg className="h-5 w-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                Skills to Develop
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {roadmap.skillGaps.skillsToDevelop?.slice(0, 15).map((skill, idx) => (
                                    <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800 font-medium">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RoadmapDetail;