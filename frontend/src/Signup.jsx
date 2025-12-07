import React, { useState } from "react";
import { auth, db } from "./firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { Loader2, Mail, Lock, Eye, EyeOff, UserPlus } from "lucide-react";

const Signup = ({ onSwitch }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState(""); // "error" or "success"
    const [loading, setLoading] = useState(false);

    const validatePassword = () => {
        if (password.length < 6) {
            setMessage("Password must be at least 6 characters long.");
            setMessageType("error");
            return false;
        }
        if (password !== confirmPassword) {
            setMessage("Passwords do not match.");
            setMessageType("error");
            return false;
        }
        return true;
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setMessageType("");

        // Validate password
        if (!validatePassword()) {
            setLoading(false);
            return;
        }

        try {
            // Create user account
            const userCred = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCred.user;

            // Save user info in Firestore
            await setDoc(doc(db, "users", user.uid), {
                email: user.email,
                createdAt: new Date(),
            });

            setMessage("Account created successfully!");
            setMessageType("success");

            // Clear form
            setEmail("");
            setPassword("");
            setConfirmPassword("");

            // Redirect to login after 2 seconds
            setTimeout(() => {
                onSwitch();
            }, 2000);

        } catch (error) {
            let errorMessage = "Signup failed. Please try again.";

            // Provide user-friendly error messages
            if (error.code === "auth/email-already-in-use") {
                errorMessage = "An account with this email already exists.";
            } else if (error.code === "auth/invalid-email") {
                errorMessage = "Invalid email address.";
            } else if (error.code === "auth/weak-password") {
                errorMessage = "Password is too weak. Use at least 6 characters.";
            } else if (error.code === "auth/network-request-failed") {
                errorMessage = "Network error. Please check your connection.";
            }

            setMessage(errorMessage);
            setMessageType("error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-4">
            <div className="w-full max-w-md">
                <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                            <UserPlus className="h-8 w-8 text-green-600" />
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
                        <p className="text-gray-600 mt-2">Start your personalized learning journey</p>
                    </div>

                    {/* Signup Form */}
                    <div className="space-y-5">
                        {/* Email Input */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    id="email"
                                    type="email"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="At least 6 characters"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                                    ) : (
                                        <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Confirm Password Input */}
                        <div>
                            <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 mb-2">
                                Confirm Password
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    id="confirm-password"
                                    type={showConfirmPassword ? "text" : "password"}
                                    placeholder="Re-enter your password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                    className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                                >
                                    {showConfirmPassword ? (
                                        <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                                    ) : (
                                        <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Password Strength Indicator */}
                        {password && (
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-xs">
                                    <div className={`h-1 flex-1 rounded ${password.length >= 6 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                    <div className={`h-1 flex-1 rounded ${password.length >= 8 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                    <div className={`h-1 flex-1 rounded ${password.length >= 10 && /[A-Z]/.test(password) && /[0-9]/.test(password) ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                </div>
                                <p className="text-xs text-gray-600">
                                    {password.length < 6 && "Weak - Use at least 6 characters"}
                                    {password.length >= 6 && password.length < 8 && "Fair - Use at least 8 characters"}
                                    {password.length >= 8 && "Good password strength"}
                                </p>
                            </div>
                        )}

                        {/* Message Display */}
                        {message && (
                            <div className={`p-4 rounded-lg ${messageType === "success"
                                    ? "bg-green-50 border border-green-200 text-green-800"
                                    : "bg-red-50 border border-red-200 text-red-800"
                                }`}>
                                <p className="text-sm font-medium">{message}</p>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            onClick={handleSignup}
                            disabled={loading}
                            className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                "Create Account"
                            )}
                        </button>
                    </div>

                    {/* Login Link */}
                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-600">
                            Already have an account?{" "}
                            <button
                                onClick={onSwitch}
                                className="font-semibold text-green-600 hover:text-green-700 transition-colors"
                            >
                                Sign in
                            </button>
                        </p>
                    </div>
                </div>

                {/* Info Box */}
                <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-xs text-green-800">
                        <strong>Tip:</strong> Use a strong password with at least 8 characters, including letters and numbers.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signup;