'use client';

import { useAuth } from '@/context/AuthContext';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { MessageSquare, Star, Calendar } from 'lucide-react';

interface UserComment {
    _id: string;
    movie_id: string;
    movie_title: string;
    text: string;
    rating?: number;
    likes: number;
    dislikes: number;
    created_at: string;
}

interface UserRating {
    _id: string;
    movie_id: string;
    movie_title: string;
    rating: number;
    text?: string;
    created_at: string;
}

export default function ProfilePage() {
    const { user, token } = useAuth();
    const [comments, setComments] = useState<UserComment[]>([]);
    const [ratings, setRatings] = useState<UserRating[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'comments' | 'ratings'>('comments');

    useEffect(() => {
        if (!user || !token) {
            window.location.href = '/login';
            return;
        }

        const fetchUserData = async () => {
            try {
                const [commentsRes, ratingsRes] = await Promise.all([
                    fetch('/api/users/me/comments', {
                        headers: { Authorization: `Bearer ${token}` }
                    }),
                    fetch('/api/users/me/ratings', {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                ]);

                if (commentsRes.ok) {
                    const commentsData = await commentsRes.json();
                    setComments(commentsData);
                }

                if (ratingsRes.ok) {
                    const ratingsData = await ratingsRes.json();
                    setRatings(ratingsData);
                }
            } catch (error) {
                console.error('Failed to fetch user data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [user, token]);

    if (!user) {
        return null;
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
            {/* Header */}
            <div style={{ marginBottom: '3rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    My Profile
                </h1>
                <p style={{ color: '#a1a1aa', fontSize: '1.1rem' }}>
                    Welcome back, <span style={{ color: '#646cff', fontWeight: 'bold' }}>{user.username}</span>
                </p>
            </div>

            {/* Stats */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.5rem',
                marginBottom: '3rem'
            }}>
                <div style={{
                    background: 'linear-gradient(135deg, #1c1c21 0%, #27272a 100%)',
                    padding: '1.5rem',
                    borderRadius: '12px',
                    border: '1px solid #27272a'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <MessageSquare size={24} color="#646cff" />
                        <h3 style={{ fontSize: '1rem', color: '#a1a1aa', margin: 0 }}>Total Comments</h3>
                    </div>
                    <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{comments.length}</p>
                </div>

                <div style={{
                    background: 'linear-gradient(135deg, #1c1c21 0%, #27272a 100%)',
                    padding: '1.5rem',
                    borderRadius: '12px',
                    border: '1px solid #27272a'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <Star size={24} color="#ffd700" />
                        <h3 style={{ fontSize: '1rem', color: '#a1a1aa', margin: 0 }}>Total Ratings</h3>
                    </div>
                    <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{ratings.length}</p>
                </div>
            </div>

            {/* Tabs */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                borderBottom: '2px solid #27272a',
                marginBottom: '2rem'
            }}>
                <button
                    onClick={() => setActiveTab('comments')}
                    style={{
                        padding: '1rem 2rem',
                        background: 'transparent',
                        border: 'none',
                        borderBottom: activeTab === 'comments' ? '2px solid #646cff' : '2px solid transparent',
                        color: activeTab === 'comments' ? '#fff' : '#a1a1aa',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        marginBottom: '-2px'
                    }}
                >
                    Comments ({comments.length})
                </button>
                <button
                    onClick={() => setActiveTab('ratings')}
                    style={{
                        padding: '1rem 2rem',
                        background: 'transparent',
                        border: 'none',
                        borderBottom: activeTab === 'ratings' ? '2px solid #646cff' : '2px solid transparent',
                        color: activeTab === 'ratings' ? '#fff' : '#a1a1aa',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        marginBottom: '-2px'
                    }}
                >
                    Ratings ({ratings.length})
                </button>
            </div>

            {/* Content */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#a1a1aa' }}>
                    Loading...
                </div>
            ) : (
                <>
                    {activeTab === 'comments' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {comments.length === 0 ? (
                                <div style={{
                                    textAlign: 'center',
                                    padding: '3rem',
                                    color: '#a1a1aa',
                                    background: '#1c1c21',
                                    borderRadius: '12px'
                                }}>
                                    No comments yet. Start discussing movies!
                                </div>
                            ) : (
                                comments.map((comment) => (
                                    <div
                                        key={comment._id}
                                        style={{
                                            background: '#1c1c21',
                                            padding: '1.5rem',
                                            borderRadius: '12px',
                                            border: '1px solid #27272a'
                                        }}
                                    >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                            <Link
                                                href={`/movie/${comment.movie_id}`}
                                                style={{
                                                    fontSize: '1.2rem',
                                                    fontWeight: 'bold',
                                                    color: '#646cff',
                                                    textDecoration: 'none'
                                                }}
                                            >
                                                {comment.movie_title}
                                            </Link>
                                            {comment.rating && (
                                                <div style={{ display: 'flex', gap: '0.25rem' }}>
                                                    {[...Array(5)].map((_, i) => (
                                                        <Star
                                                            key={i}
                                                            size={16}
                                                            fill={i < comment.rating! ? '#ffd700' : 'none'}
                                                            color={i < comment.rating! ? '#ffd700' : '#666'}
                                                        />
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                        <p style={{ color: '#e4e4e7', marginBottom: '1rem', lineHeight: '1.6' }}>
                                            {comment.text}
                                        </p>
                                        <div style={{ display: 'flex', gap: '1.5rem', color: '#a1a1aa', fontSize: '0.9rem' }}>
                                            <span>👍 {comment.likes}</span>
                                            <span>👎 {comment.dislikes}</span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                <Calendar size={14} />
                                                {formatDate(comment.created_at)}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'ratings' && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                            {ratings.length === 0 ? (
                                <div style={{
                                    gridColumn: '1 / -1',
                                    textAlign: 'center',
                                    padding: '3rem',
                                    color: '#a1a1aa',
                                    background: '#1c1c21',
                                    borderRadius: '12px'
                                }}>
                                    No ratings yet. Rate some movies!
                                </div>
                            ) : (
                                ratings.map((rating) => (
                                    <div
                                        key={rating._id}
                                        style={{
                                            background: '#1c1c21',
                                            padding: '1.5rem',
                                            borderRadius: '12px',
                                            border: '1px solid #27272a'
                                        }}
                                    >
                                        <Link
                                            href={`/movie/${rating.movie_id}`}
                                            style={{
                                                fontSize: '1.1rem',
                                                fontWeight: 'bold',
                                                color: '#646cff',
                                                textDecoration: 'none',
                                                display: 'block',
                                                marginBottom: '0.75rem'
                                            }}
                                        >
                                            {rating.movie_title}
                                        </Link>
                                        <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '0.75rem' }}>
                                            {[...Array(5)].map((_, i) => (
                                                <Star
                                                    key={i}
                                                    size={20}
                                                    fill={i < rating.rating ? '#ffd700' : 'none'}
                                                    color={i < rating.rating ? '#ffd700' : '#666'}
                                                />
                                            ))}
                                        </div>
                                        {rating.text && (
                                            <p style={{ color: '#a1a1aa', fontSize: '0.9rem', marginBottom: '0.75rem', lineHeight: '1.5' }}>
                                                {rating.text.length > 100 ? rating.text.substring(0, 100) + '...' : rating.text}
                                            </p>
                                        )}
                                        <p style={{ color: '#71717a', fontSize: '0.85rem' }}>
                                            {formatDate(rating.created_at)}
                                        </p>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
