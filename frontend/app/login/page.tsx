'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

export default function LoginPage() {
    const { login, error } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        try {
            await login(formData);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            background: '#000',
            color: '#fff',
            fontFamily: 'var(--font-geist-sans)'
        }}>
            <div style={{
                background: '#111',
                padding: '3rem',
                borderRadius: '12px',
                width: '100%',
                maxWidth: '400px',
                border: '1px solid #333'
            }}>
                <h1 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2rem', fontWeight: 'bold' }}>Login</h1>
                {error && <p style={{ color: '#ff4757', textAlign: 'center', marginBottom: '1rem' }}>{error}</p>}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{
                            padding: '1rem',
                            borderRadius: '8px',
                            border: '1px solid #333',
                            background: '#222',
                            color: '#fff',
                            fontSize: '1rem'
                        }}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            padding: '1rem',
                            borderRadius: '8px',
                            border: '1px solid #333',
                            background: '#222',
                            color: '#fff',
                            fontSize: '1rem'
                        }}
                        required
                    />
                    <button
                        type="submit"
                        style={{
                            padding: '1rem',
                            borderRadius: '8px',
                            border: 'none',
                            background: 'white',
                            color: 'black',
                            fontSize: '1rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            marginTop: '1rem'
                        }}
                    >
                        Sign In
                    </button>
                </form>
                <div style={{ marginTop: '1.5rem', textAlign: 'center', color: '#888' }}>
                    Don't have an account? <Link href="/register" style={{ color: '#fff', textDecoration: 'underline' }}>Register</Link>
                </div>
            </div>
        </div>
    );
}
