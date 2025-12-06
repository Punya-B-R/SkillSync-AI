// components/RoadmapList.jsx
import React, { useState, useEffect } from 'react';
import { getUserRoadmaps, deleteRoadmap, updateRoadmapStatus } from '../services/roadmapservice';
import { auth } from '../firebase';
import { Loader2 } from 'lucide-react';

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
                            className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${filter === status
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {status}
                            <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2.5 rounded-full text-xs">
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
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
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
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {filteredRoadmaps.map((roadmap) => (
                        <div key={roadmap.id} className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                            <div className="p-5">
                                <div className="flex items-center justify-between mb-3">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roadmap.status === 'active' ? 'bg-green-100 text-green-800' :
                                            roadmap.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                        }`}>
                                        {roadmap.status}
                                    </span>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => onViewDetail(roadmap.id)}
                                            className="text-blue-600 hover:text-blue-900"
                                            title="View Details"
                                        >
                                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={() => handleDelete(roadmap.id)}
                                            className="text-red-600 hover:text-red-900"
                                            title="Delete"
                                        >
                                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>

                                <h3 className="text-lg font-medium text-gray-900 mb-2 line-clamp-2">
                                    {roadmap.profileAnalysis?.topStrengths?.length > 0
                                        ? roadmap.profileAnalysis.topStrengths.slice(0, 2).join(', ')
                                        : roadmap.selectedTools?.length > 0
                                            ? roadmap.selectedTools.slice(0, 2).map(t => t.name).join(', ')
                                            : 'Learning Roadmap'}
                                </h3>

                                <div className="space-y-2 text-sm text-gray-600">
                                    <div className="flex items-center">
                                        <svg className="h-4 w-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        Created: {formatDate(roadmap.createdAt)}
                                    </div>
                                    <div className="flex items-center">
                                        <svg className="h-4 w-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        Duration: {roadmap.learningPlan?.estimatedWeeks || roadmap.estimatedWeeks || 'N/A'} weeks
                                    </div>
                                    <div className="flex items-center">
                                        <svg className="h-4 w-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                        </svg>
                                        Tools: {roadmap.selectedTools?.length || 0}
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                {roadmap.progress !== undefined && (
                                    <div className="mt-4">
                                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                                            <span>Progress</span>
                                            <span>{roadmap.progress}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full transition-all"
                                                style={{ width: `${roadmap.progress}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                )}

                                {/* Status Change Dropdown */}
                                <div className="mt-4">
                                    <select
                                        value={roadmap.status}
                                        onChange={(e) => handleStatusChange(roadmap.id, e.target.value)}
                                        className="block w-full pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                                    >
                                        <option value="active">Active</option>
                                        <option value="completed">Completed</option>
                                        <option value="archived">Archived</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RoadmapList;