import { initializeApp } from "firebase/app";
import { getAuth, setPersistence, browserSessionPersistence, browserLocalPersistence } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getDatabase } from "firebase/database";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const db_realtime = getDatabase(app);

// Set auth persistence to SESSION (only for current tab/window)
// Change to browserLocalPersistence if you want persistent login across sessions
setPersistence(auth, browserSessionPersistence)
    .then(() => {
        console.log("Auth persistence set to SESSION");
    })
    .catch((error) => {
        console.error("Error setting auth persistence:", error);
    });

// Export persistence options for use in Login component
export const authPersistence = {
    session: browserSessionPersistence,  // Logs out when tab/window closes
    local: browserLocalPersistence       // Stays logged in across browser restarts
};