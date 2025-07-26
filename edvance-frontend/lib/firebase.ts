// Firebase authentication service
import { initializeApp, getApps } from 'firebase/app';
import {
    getAuth,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    User
} from 'firebase/auth';

// Firebase configuration - replace with your actual config
const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);

export interface AuthResult {
    success: boolean;
    user?: User;
    idToken?: string;
    error?: string;
}

class FirebaseAuthService {
    // Sign up with email and password
    async signUp(email: string, password: string): Promise<AuthResult> {
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const idToken = await userCredential.user.getIdToken();

            return {
                success: true,
                user: userCredential.user,
                idToken,
            };
        } catch (error: any) {
            return {
                success: false,
                error: this.getErrorMessage(error.code),
            };
        }
    }

    // Sign in with email and password
    async signIn(email: string, password: string): Promise<AuthResult> {
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const idToken = await userCredential.user.getIdToken();

            return {
                success: true,
                user: userCredential.user,
                idToken,
            };
        } catch (error: any) {
            return {
                success: false,
                error: this.getErrorMessage(error.code),
            };
        }
    }

    // Sign out
    async signOut(): Promise<void> {
        await signOut(auth);
    }

    // Get current user
    getCurrentUser(): User | null {
        return auth.currentUser;
    }

    // Get current user's ID token
    async getCurrentUserToken(): Promise<string | null> {
        const user = auth.currentUser;
        if (user) {
            return await user.getIdToken();
        }
        return null;
    }

    // Listen to auth state changes
    onAuthStateChanged(callback: (user: User | null) => void) {
        return onAuthStateChanged(auth, callback);
    }

    // Convert Firebase error codes to user-friendly messages
    private getErrorMessage(errorCode: string): string {
        switch (errorCode) {
            case 'auth/user-not-found':
                return 'No user found with this email address.';
            case 'auth/wrong-password':
                return 'Incorrect password.';
            case 'auth/email-already-in-use':
                return 'An account with this email already exists.';
            case 'auth/weak-password':
                return 'Password should be at least 6 characters.';
            case 'auth/invalid-email':
                return 'Please enter a valid email address.';
            case 'auth/too-many-requests':
                return 'Too many failed attempts. Please try again later.';
            case 'auth/network-request-failed':
                return 'Network error. Please check your connection.';
            default:
                return 'An error occurred during authentication.';
        }
    }
}

export const firebaseAuth = new FirebaseAuthService();
export { auth };
