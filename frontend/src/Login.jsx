import React, { useState } from "react";
import { auth, db } from "./firebase";
import { signInWithEmailAndPassword } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";

const Login = ({ onSwitch }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const userCred = await signInWithEmailAndPassword(auth, email, password);
            const user = userCred.user;

            // Fetch user data from Firestore
            const userRef = doc(db, "users", user.uid);
            const userSnap = await getDoc(userRef);

            if (userSnap.exists()) {
                setMessage("Login successful! User: " + userSnap.data().email);
            } else {
                setMessage("User data not found in database.");
            }
        } catch (error) {
            setMessage(error.message);
        }
    };

    return (
        <div style={styles.container}>
            <h2>Login</h2>

            <form onSubmit={handleLogin} style={styles.form}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={styles.input}
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={styles.input}
                />

                <button type="submit" style={styles.button}>Login</button>
            </form>

            <p style={{ color: "red" }}>{message}</p>
            <p style={{ marginTop: "10px" }}>
                Don't have an account?
                <span
                    onClick={onSwitch}
                    style={{ color: "blue", cursor: "pointer", marginLeft: "4px" }}
                >
                    Create one
                </span>
            </p>

        </div>
    );
};

const styles = {
    container: {
        width: "300px",
        margin: "50px auto",
        textAlign: "center",
    },
    form: {
        display: "flex",
        flexDirection: "column",
        gap: "10px",
    },
    input: {
        padding: "10px",
        borderRadius: "6px",
        border: "1px solid #ccc",
    },
    button: {
        padding: "10px",
        backgroundColor: "#2196F3",
        color: "#fff",
        border: "none",
        borderRadius: "6px",
    },
};

export default Login;
