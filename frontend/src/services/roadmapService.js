// services/roadmapService.js
import {
    collection,
    addDoc,
    getDocs,
    getDoc,
    doc,
    updateDoc,
    deleteDoc,
    query,
    where,
    orderBy,
    serverTimestamp
} from 'firebase/firestore';
import { db } from '../firebase';

const ROADMAPS_COLLECTION = 'roadmaps';

/**
 * Save a new roadmap for a user
 */
export const saveRoadmap = async (userId, roadmapData) => {
    try {
        const roadmapRef = await addDoc(collection(db, ROADMAPS_COLLECTION), {
            userId,
            ...roadmapData,
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp(),
            status: 'active', // active, completed, archived
        });

        return {
            success: true,
            roadmapId: roadmapRef.id,
            message: 'Roadmap saved successfully'
        };
    } catch (error) {
        console.error('Error saving roadmap:', error);
        return {
            success: false,
            error: error.message
        };
    }
};

/**
 * Get all roadmaps for a specific user
 */
export const getUserRoadmaps = async (userId) => {
    try {
        // Try with orderBy first
        let q = query(
            collection(db, ROADMAPS_COLLECTION),
            where('userId', '==', userId),
            orderBy('createdAt', 'desc')
        );

        let querySnapshot;

        try {
            querySnapshot = await getDocs(q);
        } catch (indexError) {
            // If index error, fall back to query without orderBy
            console.warn('Index not found, querying without orderBy:', indexError);
            q = query(
                collection(db, ROADMAPS_COLLECTION),
                where('userId', '==', userId)
            );
            querySnapshot = await getDocs(q);
        }

        const roadmaps = [];

        querySnapshot.forEach((doc) => {
            roadmaps.push({
                id: doc.id,
                ...doc.data()
            });
        });

        // Sort manually if we couldn't use orderBy
        roadmaps.sort((a, b) => {
            const aTime = a.createdAt?.seconds || 0;
            const bTime = b.createdAt?.seconds || 0;
            return bTime - aTime;
        });

        return {
            success: true,
            roadmaps
        };
    } catch (error) {
        console.error('Error fetching roadmaps:', error);
        return {
            success: false,
            error: error.message,
            roadmaps: []
        };
    }
};

/**
 * Get a specific roadmap by ID
 */
export const getRoadmapById = async (roadmapId) => {
    try {
        const docRef = doc(db, ROADMAPS_COLLECTION, roadmapId);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
            return {
                success: true,
                roadmap: {
                    id: docSnap.id,
                    ...docSnap.data()
                }
            };
        } else {
            return {
                success: false,
                error: 'Roadmap not found'
            };
        }
    } catch (error) {
        console.error('Error fetching roadmap:', error);
        return {
            success: false,
            error: error.message
        };
    }
};

/**
 * Update roadmap progress
 */
export const updateRoadmapProgress = async (roadmapId, progressData) => {
    try {
        const roadmapRef = doc(db, ROADMAPS_COLLECTION, roadmapId);
        await updateDoc(roadmapRef, {
            ...progressData,
            updatedAt: serverTimestamp()
        });

        return {
            success: true,
            message: 'Progress updated successfully'
        };
    } catch (error) {
        console.error('Error updating progress:', error);
        return {
            success: false,
            error: error.message
        };
    }
};

/**
 * Delete a roadmap
 */
export const deleteRoadmap = async (roadmapId) => {
    try {
        await deleteDoc(doc(db, ROADMAPS_COLLECTION, roadmapId));
        return {
            success: true,
            message: 'Roadmap deleted successfully'
        };
    } catch (error) {
        console.error('Error deleting roadmap:', error);
        return {
            success: false,
            error: error.message
        };
    }
};

/**
 * Update roadmap status
 */
export const updateRoadmapStatus = async (roadmapId, status) => {
    try {
        const roadmapRef = doc(db, ROADMAPS_COLLECTION, roadmapId);
        await updateDoc(roadmapRef, {
            status,
            updatedAt: serverTimestamp()
        });

        return {
            success: true,
            message: 'Status updated successfully'
        };
    } catch (error) {
        console.error('Error updating status:', error);
        return {
            success: false,
            error: error.message
        };
    }
};