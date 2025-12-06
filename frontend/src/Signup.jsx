import React, { useState } from "react";
import { auth, db } from "./firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";

const Signup = ({ onSwitch }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
            const userCred = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCred.user;

            // Save user info in Firestore
            await setDoc(doc(db, "users", user.uid), {
                email: user.email,
                createdAt: new Date(),
            });

            setMessage("Signup successful!");
        } catch (error) {
            setMessage(error.message);
        }
    };

    return (
        <div style={styles.container}>
            <h2>Create Account</h2>

            <form onSubmit={handleSignup} style={styles.form}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={styles.input}
                />

                <input
                    type="password"
                    placeholder="Password (min 6 chars)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={styles.input}
                />

                <button type="submit" style={styles.button}>Sign Up</button>
            </form>

            <p style={{ color: "red" }}>{message}</p>
            <p style={{ marginTop: "10px" }}>
                Already have an account?
                <span
                    onClick={onSwitch}
                    style={{ color: "blue", cursor: "pointer", marginLeft: "4px" }}
                >
                    Login
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
        backgroundColor: "#4CAF50",
        color: "#fff",
        border: "none",
        borderRadius: "6px",
    },
};

export default Signup;
