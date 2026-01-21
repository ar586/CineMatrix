'use client';

import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';
import { User, LogOut, Home, Menu, X } from 'lucide-react';

export default function Sidebar() {
    const { user, logout } = useAuth();
    const pathname = usePathname();
    const router = useRouter();
    const [isOpen, setIsOpen] = useState(false);

    const handleLogout = () => {
        logout();
        router.push('/');
        setIsOpen(false);
    };

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    return (
        <>
            {/* Toggle Button */}
            <button
                onClick={toggleSidebar}
                style={{
                    position: 'fixed',
                    top: '1rem',
                    left: '1rem',
                    zIndex: 1000,
                    background: '#1c1c21',
                    border: '1px solid #27272a',
                    borderRadius: '8px',
                    padding: '0.5rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#27272a'}
                onMouseLeave={(e) => e.currentTarget.style.background = '#1c1c21'}
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Overlay */}
            {isOpen && (
                <div
                    onClick={() => setIsOpen(false)}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0, 0, 0, 0.5)',
                        zIndex: 998,
                        backdropFilter: 'blur(4px)'
                    }}
                />
            )}

            {/* Sidebar */}
            <div
                style={{
                    position: 'fixed',
                    top: 0,
                    left: isOpen ? 0 : '-280px',
                    width: '280px',
                    height: '100vh',
                    background: 'linear-gradient(180deg, #0a0a0c 0%, #1c1c21 100%)',
                    borderRight: '1px solid #27272a',
                    zIndex: 999,
                    transition: 'left 0.3s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '1.5rem',
                    overflowY: 'auto',
                    boxSizing: 'border-box'
                }}
            >
                {/* Header */}
                <div style={{ marginBottom: '2rem', marginTop: '3rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>CineMatrix</h2>
                    {user && (
                        <p style={{ color: '#a1a1aa', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                            Welcome, {user.username}
                        </p>
                    )}
                </div>

                {/* Navigation */}
                <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '2rem' }}>
                    <Link
                        href="/"
                        onClick={() => setIsOpen(false)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            padding: '0.75rem 1rem',
                            borderRadius: '8px',
                            textDecoration: 'none',
                            color: pathname === '/' ? '#fff' : '#a1a1aa',
                            background: pathname === '/' ? '#27272a' : 'transparent',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            if (pathname !== '/') e.currentTarget.style.background = '#1c1c21';
                        }}
                        onMouseLeave={(e) => {
                            if (pathname !== '/') e.currentTarget.style.background = 'transparent';
                        }}
                    >
                        <Home size={20} />
                        <span>Home</span>
                    </Link>

                    {user && (
                        <Link
                            href="/profile"
                            onClick={() => setIsOpen(false)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                padding: '0.75rem 1rem',
                                borderRadius: '8px',
                                textDecoration: 'none',
                                color: pathname === '/profile' ? '#fff' : '#a1a1aa',
                                background: pathname === '/profile' ? '#27272a' : 'transparent',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => {
                                if (pathname !== '/profile') e.currentTarget.style.background = '#1c1c21';
                            }}
                            onMouseLeave={(e) => {
                                if (pathname !== '/profile') e.currentTarget.style.background = 'transparent';
                            }}
                        >
                            <User size={20} />
                            <span>Profile</span>
                        </Link>
                    )}
                </nav>

                {/* Auth Section */}
                <div style={{ borderTop: '1px solid #27272a', paddingTop: '1rem' }}>
                    {user ? (
                        <button
                            onClick={handleLogout}
                            style={{
                                width: '100%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem',
                                background: '#ff4757',
                                border: 'none',
                                borderRadius: '8px',
                                color: '#fff',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#ff3838'}
                            onMouseLeave={(e) => e.currentTarget.style.background = '#ff4757'}
                        >
                            <LogOut size={20} />
                            <span>Logout</span>
                        </button>
                    ) : (
                        <Link
                            href="/login"
                            onClick={() => setIsOpen(false)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem',
                                background: '#646cff',
                                borderRadius: '8px',
                                textDecoration: 'none',
                                color: '#fff',
                                fontWeight: 'bold',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#535bf2'}
                            onMouseLeave={(e) => e.currentTarget.style.background = '#646cff'}
                        >
                            <User size={20} />
                            <span>Login</span>
                        </Link>
                    )}
                </div>
            </div>
        </>
    );
}
