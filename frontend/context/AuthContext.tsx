'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '@/services/api';
import { useRouter } from 'next/navigation';

interface User {
    username: string;
    email?: string;
    full_name?: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (formData: FormData) => Promise<void>;
    register: (data: any) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
    error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Check local storage on mount
        const storedToken = localStorage.getItem('access_token');
        if (storedToken) {
            setToken(storedToken);
            api.getMe(storedToken)
                .then(u => setUser(u))
                .catch(() => {
                    localStorage.removeItem('access_token');
                    setToken(null);
                })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = async (formData: FormData) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.login(formData);
            const accessToken = data.access_token;
            localStorage.setItem('access_token', accessToken);
            setToken(accessToken);

            // Fetch user details
            const userData = await api.getMe(accessToken);
            setUser(userData);

            router.push('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (userData: any) => {
        setIsLoading(true);
        setError(null);
        try {
            await api.register(userData);
            // Auto login after register? Or redirect to login?
            // Let's redirect to login for now, or auto login logic
            // Converting userData to FormData for login is tricky if password is hashed or plain
            // Simple flow: Redirect to login
            router.push('/login');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setToken(null);
        setUser(null);
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, isLoading, error }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
