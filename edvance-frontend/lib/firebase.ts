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
import { getFirestore, doc, getDoc, collection, query, where, getDocs } from 'firebase/firestore';

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
const db = getFirestore(app);

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

    // Student authentication using Firestore
    async authenticateStudent(userId: string, password: string): Promise<{
        success: boolean;
        student?: any;
        token?: string;
        error?: string;
    }> {
        try {
            console.log('Attempting to authenticate student:', userId);

            // Query the students collection for the provided user ID
            const studentsRef = collection(db, 'students');
            const q = query(studentsRef, where('student_id', '==', userId));
            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                console.log('No student found with ID:', userId);
                return {
                    success: false,
                    error: 'Student ID not found'
                };
            }

            // Get the first (and should be only) matching student
            const studentDoc = querySnapshot.docs[0];
            const studentData = studentDoc.data();
            console.log('Found student data:', {
                student_id: studentData.student_id,
                first_name: studentData.first_name,
                is_active: studentData.is_active
            });

            // Check if the password matches the default password
            if (password !== studentData.default_password) {
                console.log('Password mismatch for student:', userId);
                return {
                    success: false,
                    error: 'Invalid password'
                };
            }

            // Check if student is active
            if (!studentData.is_active) {
                console.log('Student account is inactive:', userId);
                return {
                    success: false,
                    error: 'Student account is inactive'
                };
            }

            // Generate a simple session token (in production, use a more secure method)
            const sessionToken = studentData.current_session_token || this.generateSessionToken();
            console.log('Student authentication successful:', userId);

            return {
                success: true,
                student: {
                    id: studentDoc.id,
                    student_id: studentData.student_id,
                    first_name: studentData.first_name,
                    last_name: studentData.last_name,
                    grade: studentData.grade,
                    subjects: studentData.subjects,
                    teacher_uid: studentData.teacher_uid,
                    ...studentData
                },
                token: sessionToken
            };

        } catch (error: any) {
            console.error('Student authentication error:', error);

            // Check if it's a permissions error
            if (error.code === 'permission-denied') {
                return {
                    success: false,
                    error: 'Database access denied. Please contact your administrator to update Firebase security rules.'
                };
            }

            // Check if it's a network error
            if (error.code === 'unavailable') {
                return {
                    success: false,
                    error: 'Database temporarily unavailable. Please try again later.'
                };
            }

            return {
                success: false,
                error: `Authentication failed: ${error.message || 'Please try again.'}`
            };
        }
    }

    // Generate a simple session token (in production, use JWT or similar)
    private generateSessionToken(): string {
        return btoa(`${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
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
export { auth, db };
