import React, { useState, useEffect } from 'react';
import { getRoadmapById, updateRoadmapProgress } from '../services/roadmapservice';
import { Check, Clock, Calendar, BookOpen, Target, ChevronDown, ChevronUp, Loader2, AlertCircle, TrendingUp } from 'lucide-react';

const RoadmapDetail = ({ roadmapId, onBack }) => {
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [lastSaved, setLastSaved] = useState(null);
    const [showSavedMessage, setShowSavedMessage] = useState(false);

    useEffect(() => {
        fetchRoadmap();
    }, [roadmapId]);

    useEffect(() => {
        if (lastSaved) {
            setShowSavedMessage(true);
            const timer = setTimeout(() => setShowSavedMessage(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [lastSaved]);

    const fetchRoadmap = async () => {
        setLoading(true);
        setError(null);

        const result = await getRoadmapById(roadmapId);

        if (result.success) {
            // Initialize progress tracking if not exists
            const roadmapData = result.roadmap;

            if (!roadmapData.phases || roadmapData.phases.length === 0) {
                // Create phases from learningResources if phases don't exist
                if (roadmapData.learningResources && roadmapData.learningResources.length > 0) {
                    roadmapData.phases = roadmapData.learningResources.map((resource, idx) => ({
                        id: `phase-${idx + 1}`,
                        phase_number: resource.phase_number || idx + 1,
                        title: resource.toolName || `Phase ${idx + 1}`,
                        duration_weeks: resource.duration_weeks || 4,
                        tools_covered: resource.tools_covered || [resource.toolName],
                        learning_objectives: resource.learning_objectives || [],
                        milestones: resource.milestones || [],
                        expanded: idx === 0
                    }));
                }
            }

            // Initialize checkboxes for objectives and milestones if not exists
            roadmapData.phases = roadmapData.phases.map(phase => ({
                ...phase,
                learning_objectives: (phase.learning_objectives || []).map(obj =>
                    typeof obj === 'string'
                        ? { id: `obj-${Date.now()}-${Math.random()}`, text: obj, completed: false }
                        : obj
                ),
                milestones: (phase.milestones || []).map(ms =>
                    typeof ms === 'string'
                        ? { id: `ms-${Date.now()}-${Math.random()}`, text: ms, completed: false }
                        : ms
                )
            }));

            setRoadmap(roadmapData);
        } else {
            setError(result.error || 'Failed to load roadmap');
        }

        setLoading(false);
    };

    const calculateProgress = () => {
        if (!roadmap || !roadmap.phases) return 0;

        let totalItems = 0;
        let completedItems = 0;

        roadmap.phases.forEach(phase => {
            (phase.learning_objectives || []).forEach(obj => {
                totalItems++;
                if (obj.completed) completedItems++;
            });
            (phase.milestones || []).forEach(ms => {
                totalItems++;
                if (ms.completed) completedItems++;
            });
        });

        return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
    };

    const getPhaseProgress = (phase) => {
        const objectives = phase.learning_objectives || [];
        const milestones = phase.milestones || [];
        const total = objectives.length + milestones.length;

        if (total === 0) return 0;

        const completed =
            objectives.filter(obj => obj.completed).length +
            milestones.filter(ms => ms.completed).length;

        return Math.round((completed / total) * 100);
    };

    const toggleObjective = async (phaseId, objectiveId) => {
        const updatedRoadmap = {
            ...roadmap,
            phases: roadmap.phases.map(phase => {
                if (phase.id === phaseId) {
                    return {
                        ...phase,
                        learning_objectives: phase.learning_objectives.map(obj =>
                            obj.id === objectiveId ? { ...obj, completed: !obj.completed } : obj
                        )
                    };
                }
                return phase;
            })
        };

        setRoadmap(updatedRoadmap);
        await saveProgress(updatedRoadmap);
    };

    const toggleMilestone = async (phaseId, milestoneId) => {
        const updatedRoadmap = {
            ...roadmap,
            phases: roadmap.phases.map(phase => {
                if (phase.id === phaseId) {
                    return {
                        ...phase,
                        milestones: phase.milestones.map(ms =>
                            ms.id === milestoneId ? { ...ms, completed: !ms.completed } : ms
                        )
                    };
                }
                return phase;
            })
        };

        setRoadmap(updatedRoadmap);
        await saveProgress(updatedRoadmap);
    };

    const togglePhaseExpansion = (phaseId) => {
        setRoadmap(prev => ({
            ...prev,
            phases: prev.phases.map(phase =>
                phase.id === phaseId ? { ...phase, expanded: !phase.expanded } : phase
            )
        }));
    };

    const saveProgress = async (updatedRoadmap) => {
        setSaving(true);

        const progress = calculateProgressFromRoadmap(updatedRoadmap);

        const progressData = {
            phases: updatedRoadmap.phases,
            progress: progress
        };

        const result = await updateRoadmapProgress(roadmapId, progressData);

        if (result.success) {
            setLastSaved(new Date());
        } else {
            setError('Failed to save progress');
            setTimeout(() => setError(null), 3000);
        }

        setSaving(false);
    };

    const calculateProgressFromRoadmap = (roadmapData) => {
        let totalItems = 0;
        let completedItems = 0;

        (roadmapData.phases || []).forEach(phase => {
            (phase.learning_objectives || []).forEach(obj => {
                totalItems++;
                if (obj.completed) completedItems++;
            });
            (phase.milestones || []).forEach(ms => {
                totalItems++;
                if (ms.completed) completedItems++;
            });
        });

        return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading roadmap details...</p>
                </div>
            </div>
        );
    }

    if (error && !roadmap) {
        return (
            <div className="min-h-screen flex items-center justify-center p-4">
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 max-w-md">
                    <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-red-900 mb-2 text-center">Error Loading Roadmap</h3>
                    <p className="text-red-700 text-center mb-4">{error}</p>
                    <button
                        onClick={onBack}
                        className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    if (!roadmap) {
        return (
            <div className="min-h-screen flex items-center justify-center p-4">
                <div className="text-center">
                    <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Roadmap Not Found</h3>
                    <button
                        onClick={onBack}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    const overallProgress = calculateProgress();
    const totalPhases = roadmap.phases?.length || 0;
    const completedPhases = roadmap.phases?.filter(p => getPhaseProgress(p) === 100).length || 0;

    return (
        <div className="max-w-5xl mx-auto p-6">
            {/* Saving Indicator */}
            {saving && (
                <div className="fixed top-20 right-6 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-fade-in">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Saving progress...</span>
                </div>
            )}

            {/* Last Saved Indicator */}
            {showSavedMessage && !saving && (
                <div className="fixed top-20 right-6 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-fade-in">
                    <Check className="h-4 w-4" />
                    <span className="text-sm">Progress saved!</span>
                </div>
            )}

            {/* Error Message */}
            {error && roadmap && (
                <div className="fixed top-20 right-6 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-fade-in">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm">{error}</span>
                </div>
            )}

            {/* Overall Progress Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-slate-200">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h2 className="text-2xl font-bold text-slate-900">Overall Progress</h2>
                        <p className="text-slate-600 text-sm mt-1">Your Learning Journey</p>
                    </div>
                    <div className="text-right">
                        <div className="text-4xl font-bold text-blue-600">{overallProgress}%</div>
                        <span className="text-xs text-slate-500 uppercase tracking-wide">Complete</span>
                    </div>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-3 mb-6">
                    <div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${overallProgress}%` }}
                    />
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-blue-50 rounded-lg">
                            <Check className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <div className="text-sm text-slate-600">Completed</div>
                            <div className="text-xl font-semibold text-slate-900">
                                {roadmap.phases?.reduce((acc, p) =>
                                    acc + (p.learning_objectives?.filter(o => o.completed).length || 0) +
                                    (p.milestones?.filter(m => m.completed).length || 0), 0)} /
                                {roadmap.phases?.reduce((acc, p) =>
                                    acc + (p.learning_objectives?.length || 0) + (p.milestones?.length || 0), 0)}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-purple-50 rounded-lg">
                            <Clock className="w-5 h-5 text-purple-600" />
                        </div>
                        <div>
                            <div className="text-sm text-slate-600">Duration</div>
                            <div className="text-xl font-semibold text-slate-900">
                                {roadmap.learningPlan?.estimatedWeeks || roadmap.estimatedWeeks || 'N/A'} weeks
                            </div>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-amber-50 rounded-lg">
                            <Calendar className="w-5 h-5 text-amber-600" />
                        </div>
                        <div>
                            <div className="text-sm text-slate-600">Hours/Week</div>
                            <div className="text-xl font-semibold text-slate-900">
                                {roadmap.learningPreferences?.hoursPerWeek || roadmap.learningPlan?.hoursPerWeek || 6} hrs
                            </div>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-green-50 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                            <div className="text-sm text-slate-600">Phases Done</div>
                            <div className="text-xl font-semibold text-slate-900">
                                {completedPhases} / {totalPhases}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Learning Path */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-slate-200">
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Learning Path</h2>

                <div className="space-y-4">
                    {roadmap.phases?.map((phase, index) => {
                        const phaseProgress = getPhaseProgress(phase);

                        return (
                            <div key={phase.id} className="border border-slate-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                                {/* Phase Header */}
                                <div
                                    className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 cursor-pointer hover:from-slate-100 hover:to-blue-100 transition-colors"
                                    onClick={() => togglePhaseExpansion(phase.id)}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4 flex-1">
                                            <div className="flex items-center justify-center w-10 h-10 bg-blue-600 text-white rounded-full font-semibold">
                                                P{phase.phase_number || index + 1}
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="font-semibold text-slate-900 mb-1">{phase.title}</h3>
                                                <div className="flex items-center gap-4 text-sm text-slate-600">
                                                    <span className="flex items-center gap-1">
                                                        <Clock className="w-4 h-4" />
                                                        {phase.duration_weeks} weeks
                                                    </span>
                                                    {phase.tools_covered && phase.tools_covered.length > 0 && (
                                                        <span className="flex gap-1 flex-wrap">
                                                            {phase.tools_covered.slice(0, 2).map((tool, i) => (
                                                                <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                                                                    {tool}
                                                                </span>
                                                            ))}
                                                            {phase.tools_covered.length > 2 && (
                                                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                                                                    +{phase.tools_covered.length - 2}
                                                                </span>
                                                            )}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className="text-2xl font-bold text-blue-600">{phaseProgress}%</div>
                                                {phaseProgress === 100 && (
                                                    <span className="text-xs text-green-600 font-medium">Complete!</span>
                                                )}
                                            </div>
                                            {phase.expanded ?
                                                <ChevronUp className="w-5 h-5 text-slate-400" /> :
                                                <ChevronDown className="w-5 h-5 text-slate-400" />
                                            }
                                        </div>
                                    </div>

                                    <div className="mt-3">
                                        <div className="w-full bg-slate-200 rounded-full h-2">
                                            <div
                                                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${phaseProgress}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Phase Content */}
                                {phase.expanded && (
                                    <div className="p-6 bg-white">
                                        {/* Learning Objectives */}
                                        {phase.learning_objectives && phase.learning_objectives.length > 0 && (
                                            <div className="mb-6">
                                                <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                                    <Target className="w-5 h-5 text-blue-600" />
                                                    Learning Objectives
                                                </h4>
                                                <div className="space-y-2">
                                                    {phase.learning_objectives.map(objective => (
                                                        <label
                                                            key={objective.id}
                                                            className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors group"
                                                        >
                                                            <input
                                                                type="checkbox"
                                                                checked={objective.completed || false}
                                                                onChange={() => toggleObjective(phase.id, objective.id)}
                                                                className="mt-1 w-5 h-5 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                                                            />
                                                            <span className={`flex-1 transition-all ${objective.completed ? 'line-through text-slate-400' : 'text-slate-700'}`}>
                                                                {objective.text}
                                                            </span>
                                                            {objective.completed && (
                                                                <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                                                                    ✓ Done
                                                                </span>
                                                            )}
                                                        </label>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Milestones */}
                                        {phase.milestones && phase.milestones.length > 0 && (
                                            <div>
                                                <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                                                    <Check className="w-5 h-5 text-green-600" />
                                                    Milestones
                                                </h4>
                                                <div className="space-y-2">
                                                    {phase.milestones.map(milestone => (
                                                        <label
                                                            key={milestone.id}
                                                            className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors group"
                                                        >
                                                            <input
                                                                type="checkbox"
                                                                checked={milestone.completed || false}
                                                                onChange={() => toggleMilestone(phase.id, milestone.id)}
                                                                className="mt-1 w-5 h-5 text-green-600 border-slate-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
                                                            />
                                                            <span className={`flex-1 transition-all ${milestone.completed ? 'line-through text-slate-400' : 'text-slate-700'}`}>
                                                                {milestone.text}
                                                            </span>
                                                            {milestone.completed && (
                                                                <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                                                                    ✓ Achieved
                                                                </span>
                                                            )}
                                                        </label>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default RoadmapDetail;