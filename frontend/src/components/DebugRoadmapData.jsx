// components/DebugRoadmapData.jsx
// Temporary component to help debug what data is being passed
import React, { useState } from 'react';

const DebugRoadmapData = ({ profile, selectedTools, preferences, roadmap }) => {
    const [isOpen, setIsOpen] = useState(false);

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-4 left-4 bg-purple-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-purple-700 z-50"
            >
                🐛 Debug Data
            </button>
        );
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-gray-900">Debug Roadmap Data</h2>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Profile Data */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Profile Data</h3>
                        <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(profile, null, 2)}
                        </pre>
                    </div>

                    {/* Selected Tools */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Selected Tools ({selectedTools?.length || 0})
                        </h3>
                        <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(selectedTools, null, 2)}
                        </pre>
                    </div>

                    {/* Preferences */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Preferences</h3>
                        <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(preferences, null, 2)}
                        </pre>
                    </div>

                    {/* Roadmap */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Roadmap Data
                        </h3>
                        <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(roadmap, null, 2)}
                        </pre>
                    </div>

                    {/* Key Checks */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Checks</h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex items-center gap-2">
                                {selectedTools?.length > 0 ? (
                                    <span className="text-green-600">✓</span>
                                ) : (
                                    <span className="text-red-600">✗</span>
                                )}
                                <span>selectedTools has {selectedTools?.length || 0} items</span>
                            </div>
                            <div className="flex items-center gap-2">
                                {roadmap?.learning_resources?.length > 0 || roadmap?.learningResources?.length > 0 ? (
                                    <span className="text-green-600">✓</span>
                                ) : (
                                    <span className="text-red-600">✗</span>
                                )}
                                <span>Roadmap has learning resources</span>
                            </div>
                            <div className="flex items-center gap-2">
                                {profile?.technical_skills?.length > 0 ? (
                                    <span className="text-green-600">✓</span>
                                ) : (
                                    <span className="text-red-600">✗</span>
                                )}
                                <span>Profile has technical skills</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DebugRoadmapData;