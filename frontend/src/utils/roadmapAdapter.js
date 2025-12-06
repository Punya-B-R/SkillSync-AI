// utils/roadmapAdapter.js
// Add this utility file to handle different backend response formats

/**
 * Adapts backend API response to consistent frontend format
 * Handles both snake_case and camelCase field names
 */
export const adaptRoadmapData = (roadmapResponse) => {
    if (!roadmapResponse) return null;

    return {
        // Handle both formats for estimated weeks
        estimatedWeeks: roadmapResponse.estimated_weeks || roadmapResponse.estimatedWeeks || 0,

        // Handle both formats for learning resources
        learningResources: roadmapResponse.learning_resources || roadmapResponse.learningResources || [],

        // Handle both formats for project ideas
        projectIdeas: roadmapResponse.project_ideas || roadmapResponse.projectIdeas || [],

        // Handle both formats for career insights
        careerInsights: roadmapResponse.career_insights || roadmapResponse.careerInsights || {},

        // Include any other fields from the response
        ...roadmapResponse
    };
};

/**
 * Adapts tool data to consistent format
 */
export const adaptToolData = (tool) => {
    if (!tool) return null;

    return {
        name: tool.name || tool.tool_name || tool.toolName || 'Unknown Tool',
        category: tool.category || 'General',
        difficulty: tool.difficulty || 'Moderate',
        estimatedTime: tool.estimated_time || tool.estimatedTime || tool.duration || 'N/A'
    };
};

/**
 * Adapts profile data to consistent format
 */
export const adaptProfileData = (profile) => {
    if (!profile) return null;

    return {
        experienceLevel: profile.experience_level || profile.experienceLevel || 'Junior',
        yearsOfExperience: profile.years_of_experience || profile.yearsOfExperience || 0,
        technicalSkills: profile.technical_skills || profile.technicalSkills || [],
        topStrengths: profile.top_strengths || profile.topStrengths || [],
        domainExpertise: profile.domain_expertise || profile.domainExpertise || []
    };
};

/**
 * Validates that roadmap has minimum required data
 */
export const validateRoadmapData = (roadmapData) => {
    const errors = [];

    if (!roadmapData.selectedTools || roadmapData.selectedTools.length === 0) {
        errors.push('No tools selected');
    }

    if (!roadmapData.profileAnalysis || Object.keys(roadmapData.profileAnalysis).length === 0) {
        errors.push('Profile analysis missing');
    }

    if (!roadmapData.learningPreferences) {
        errors.push('Learning preferences missing');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};

/**
 * Example usage in App.jsx:
 * 
 * import { adaptRoadmapData, adaptToolData, validateRoadmapData } from './utils/roadmapAdapter';
 * 
 * // After getting API response
 * const response = await generateRoadmap(userData);
 * if (response.success) {
 *   const adaptedRoadmap = adaptRoadmapData(response.roadmap);
 *   setRoadmap(adaptedRoadmap);
 * }
 * 
 * // Before saving to Firebase
 * const validation = validateRoadmapData(roadmapToSave);
 * if (!validation.isValid) {
 *   console.error('Validation errors:', validation.errors);
 *   return;
 * }
 */