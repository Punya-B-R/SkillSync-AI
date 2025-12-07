import React, { useState, useEffect } from 'react';
import { getUserRoadmaps, deleteRoadmap, updateRoadmapStatus } from '../services/roadmapService';
import { auth } from '../firebase';
import { Loader2, Eye, Trash2, Calendar, Clock, BookOpen, TrendingUp } from 'lucide-react';

const RoadmapList = ({ onViewDetail, onBackToGenerator }) => {
    const [roadmaps, setRoadmaps] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const currentUser = auth.currentUser;

    useEffect(() => {
        fetchRoadmaps();
    }, [currentUser]);

    const fetchRoadmaps = async () => {
        if (!currentUser) return;

        setLoading(true);
        const result = await getUserRoadmaps(currentUser.uid);

        if (result.success) {
            console.log('Fetched roadmaps:', result.roadmaps);
            setRoadmaps(result.roadmaps);
        } else {
            console.error('Failed to fetch roadmaps:', result.error);
        }
        setLoading(false);
    };

    const handleDelete = async (roadmapId) => {
        if (window.confirm('Are you sure you want to delete this roadmap?')) {
            const result = await deleteRoadmap(roadmapId);
            if (result.success) {
                fetchRoadmaps();
            }
        }
    };

    const handleStatusChange = async (roadmapId, newStatus) => {
        const result = await updateRoadmapStatus(roadmapId, newStatus);
        if (result.success) {
            fetchRoadmaps();
        }
    };

    const filteredRoadmaps = roadmaps.filter(roadmap =>
        filter === 'all' ? true : roadmap.status === filter
    );

    const formatDate = (timestamp) => {
        if (!timestamp) return 'N/A';
        return new Date(timestamp.seconds * 1000).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    // Get roadmap title from various possible sources
    const getRoadmapTitle = (roadmap) => {
        if (roadmap.selectedTools && roadmap.selectedTools.length > 0) {
            return roadmap.selectedTools.slice(0, 2).map(t => t.name).join(', ');
        }
        if (roadmap.profileAnalysis?.topStrengths && roadmap.profileAnalysis.topStrengths.length > 0) {
            return roadmap.profileAnalysis.topStrengths.slice(0, 2).join(', ');
        }
        if (roadmap.phases && roadmap.phases.length > 0) {
            return roadmap.phases[0].title || 'Learning Roadmap';
        }
        return 'Learning Roadmap';
    };

    const getProgressStats = (roadmap) => {
        const progress = roadmap.progress || 0;
        let completedItems = 0;
        let totalItems = 0;

        if (roadmap.phases && Array.isArray(roadmap.phases)) {
            roadmap.phases.forEach(phase => {
                if (phase.learning_objectives) {
                    phase.learning_objectives.forEach(obj => {
                        totalItems++;
                        if (obj.completed) completedItems++;
                    });
                }
                if (phase.milestones) {
                    phase.milestones.forEach(ms => {
                        totalItems++;
                        if (ms.completed) completedItems++;
                    });
                }
            });
        }

        return {
            progress,
            completedItems,
            totalItems
        };
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading your roadmaps...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Filter Tabs */}
            <div className="mb-6 border-b border-gray-200">
                <nav className="flex space-x-8">
                    {['all', 'active', 'completed', 'archived'].map((status) => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            className={`py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${filter === status
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {status}
                            <span className={`ml-2 py-0.5 px-2.5 rounded-full text-xs ${filter === status
                                ? 'bg-blue-100 text-blue-600'
                                : 'bg-gray-100 text-gray-600'
                                }`}>
                                {status === 'all'
                                    ? roadmaps.length
                                    : roadmaps.filter(r => r.status === status).length
                                }
                            </span>
                        </button>
                    ))}
                </nav>
            </div>

            {/* Roadmaps Grid */}
            {filteredRoadmaps.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg shadow">
                    <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No roadmaps found</h3>
                    <p className="mt-1 text-sm text-gray-500">
                        {filter === 'all'
                            ? 'Get started by creating your first roadmap.'
                            : `No ${filter} roadmaps yet.`}
                    </p>
                    <button
                        onClick={onBackToGenerator}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Create Your First Roadmap
                    </button>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
                    {filteredRoadmaps.map((roadmap) => {
                        const stats = getProgressStats(roadmap);

                        return (
                            <div
                                key={roadmap.id}
                                className="bg-white overflow-hidden shadow rounded-xl hover:shadow-xl transition-all border border-gray-200 hover:border-blue-300"
                            >
                                <div className="p-6">
                                    {/* Header */}
                                    <div className="flex items-start justify-between mb-4">
                                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${roadmap.status === 'active' ? 'bg-green-100 text-green-800' :
                                            roadmap.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                            {roadmap.status}
                                        </span>
                                        <div className="flex space-x-2">
                                            <button
                                                onClick={() => onViewDetail(roadmap.id)}
                                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                title="View Details"
                                            >
                                                <Eye className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(roadmap.id)}
                                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                title="Delete"
                                            >
                                                <Trash2 className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </div>

                                    {/* Title */}
                                    <h3 className="text-xl font-bold text-gray-900 mb-4 line-clamp-2">
                                        {getRoadmapTitle(roadmap)}
                                    </h3>

                                    {/* Progress Section */}
                                    <div className="mb-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-medium text-gray-700">Progress</span>
                                            <span className="text-2xl font-bold text-blue-600">{stats.progress}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3">
                                            <div
                                                className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                                                style={{ width: `${stats.progress}%` }}
                                            ></div>
                                        </div>
                                        {stats.totalItems > 0 && (
                                            <p className="text-xs text-gray-500 mt-1">
                                                {stats.completedItems} of {stats.totalItems} tasks completed
                                            </p>
                                        )}
                                    </div>

                                    {/* Info Grid */}
                                    <div className="grid grid-cols-2 gap-3 mb-4">
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                            <Calendar className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <p className="text-xs text-gray-500">Created</p>
                                                <p className="font-medium">{formatDate(roadmap.createdAt)}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                            <Clock className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <p className="text-xs text-gray-500">Duration</p>
                                                <p className="font-medium">
                                                    {roadmap.learningPlan?.estimatedWeeks || roadmap.estimatedWeeks || 'N/A'} weeks
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                            <BookOpen className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <p className="text-xs text-gray-500">Tools</p>
                                                <p className="font-medium">{roadmap.selectedTools?.length || 0}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                            <TrendingUp className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <p className="text-xs text-gray-500">Hours/Week</p>
                                                <p className="font-medium">
                                                    {roadmap.learningPreferences?.hoursPerWeek ||
                                                        roadmap.learningPlan?.hoursPerWeek || 6} hrs
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Tools/Phases */}
                                    {roadmap.selectedTools && roadmap.selectedTools.length > 0 && (
                                        <div className="mb-4">
                                            <p className="text-xs text-gray-500 mb-2">Learning</p>
                                            <div className="flex flex-wrap gap-1">
                                                {roadmap.selectedTools.slice(0, 3).map((tool, idx) => (
                                                    <span key={idx} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                                                        {tool.name}
                                                    </span>
                                                ))}
                                                {roadmap.selectedTools.length > 3 && (
                                                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                                                        +{roadmap.selectedTools.length - 3} more
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    {/* Status Dropdown */}
                                    <select
                                        value={roadmap.status}
                                        onChange={(e) => handleStatusChange(roadmap.id, e.target.value)}
                                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                                    >
                                        <option value="active">Active</option>
                                        <option value="completed">Completed</option>
                                        <option value="archived">Archived</option>
                                    </select>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default RoadmapList;