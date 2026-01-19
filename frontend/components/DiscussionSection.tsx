'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { ThumbsUp, ThumbsDown, MoreVertical } from 'lucide-react';

interface Comment {
    _id: string;
    username: string;
    text: string;
    rating?: number;
    created_at: string;
}

interface DiscussionSectionProps {
    movieId: string;
}

const timeAgo = (date: string) => {
    const seconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";
    return "just now";
};

export default function DiscussionSection({ movieId }: DiscussionSectionProps) {
    const { user, token } = useAuth();
    const [comments, setComments] = useState<Comment[]>([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchComments();
    }, [movieId]);

    const fetchComments = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/movies/${movieId}/comments/`);
            if (res.ok) {
                const data = await res.json();
                setComments(data.filter((c: Comment) => c.text && c.text.trim().length > 0));
            }
        } catch (err) {
            console.error("Failed to fetch comments", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token || !newComment.trim()) return;

        setSubmitting(true);
        setError('');

        try {
            const res = await fetch(`http://localhost:8000/api/movies/${movieId}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    text: newComment
                })
            });

            if (res.ok) {
                const comment = await res.json();
                setComments([comment, ...comments]);
                setNewComment('');
            } else {
                const errData = await res.json();
                setError(errData.detail || 'Failed to post comment');
            }
        } catch (err) {
            setError('An error occurred');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={{ padding: '24px 0' }}>

            {/* Comments Count Header - YouTube Style */}
            <div style={{ marginBottom: '32px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: '400', margin: 0, color: '#f1f1f1' }}>
                    {comments.length} Comments
                </h2>
            </div>

            {/* Add Comment - YouTube Style */}
            {user ? (
                <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
                    {/* User Avatar */}
                    <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontSize: '16px',
                        fontWeight: '500',
                        flexShrink: 0
                    }}>
                        {user.username.charAt(0).toUpperCase()}
                    </div>

                    {/* Comment Input */}
                    <div style={{ flex: 1 }}>
                        <form onSubmit={handleSubmit}>
                            <input
                                type="text"
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                                placeholder="Add a comment..."
                                style={{
                                    width: '100%',
                                    background: 'transparent',
                                    border: 'none',
                                    borderBottom: '1px solid #303030',
                                    color: '#f1f1f1',
                                    fontSize: '14px',
                                    padding: '8px 0',
                                    outline: 'none',
                                    transition: 'border-color 0.2s'
                                }}
                                onFocus={(e) => e.target.style.borderBottomColor = '#aaa'}
                                onBlur={(e) => e.target.style.borderBottomColor = '#303030'}
                                required
                            />
                            {newComment.trim() && (
                                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                                    <button
                                        type="button"
                                        onClick={() => setNewComment('')}
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: '#aaa',
                                            padding: '10px 16px',
                                            borderRadius: '18px',
                                            fontSize: '14px',
                                            fontWeight: '500',
                                            cursor: 'pointer',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                        style={{
                                            background: '#3ea6ff',
                                            border: 'none',
                                            color: '#0f0f0f',
                                            padding: '10px 16px',
                                            borderRadius: '18px',
                                            fontSize: '14px',
                                            fontWeight: '500',
                                            cursor: submitting ? 'not-allowed' : 'pointer',
                                            opacity: submitting ? 0.5 : 1,
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={(e) => !submitting && (e.currentTarget.style.background = '#65b8ff')}
                                        onMouseLeave={(e) => !submitting && (e.currentTarget.style.background = '#3ea6ff')}
                                    >
                                        Comment
                                    </button>
                                </div>
                            )}
                        </form>
                        {error && <p style={{ color: '#f44336', fontSize: '12px', marginTop: '8px' }}>{error}</p>}
                    </div>
                </div>
            ) : (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '16px',
                    background: '#212121',
                    borderRadius: '8px',
                    marginBottom: '32px'
                }}>
                    <span style={{ color: '#aaa', fontSize: '14px' }}>Sign in to comment</span>
                    <a
                        href="/login"
                        style={{
                            background: '#3ea6ff',
                            color: '#0f0f0f',
                            padding: '8px 16px',
                            borderRadius: '18px',
                            fontSize: '14px',
                            fontWeight: '500',
                            textDecoration: 'none',
                            marginLeft: 'auto'
                        }}
                    >
                        Sign in
                    </a>
                </div>
            )}

            {/* Comments List - YouTube Style */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#aaa' }}>
                    Loading comments...
                </div>
            ) : comments.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#aaa' }}>
                    <p style={{ fontSize: '14px', margin: 0 }}>No comments yet</p>
                </div>
            ) : (
                <div>
                    {comments.map((comment) => (
                        <div
                            key={comment._id}
                            style={{
                                display: 'flex',
                                gap: '16px',
                                marginBottom: '16px',
                                padding: '12px 0'
                            }}
                        >
                            {/* Avatar */}
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '50%',
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: '#fff',
                                fontSize: '16px',
                                fontWeight: '500',
                                flexShrink: 0
                            }}>
                                {comment.username.charAt(0).toUpperCase()}
                            </div>

                            {/* Comment Content */}
                            <div style={{ flex: 1, minWidth: 0 }}>
                                {/* Username and Time */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                    <span style={{ fontSize: '13px', fontWeight: '500', color: '#f1f1f1' }}>
                                        @{comment.username}
                                    </span>
                                    <span style={{ fontSize: '12px', color: '#aaa' }}>
                                        {timeAgo(comment.created_at)}
                                    </span>
                                </div>

                                {/* Comment Text */}
                                <p style={{
                                    fontSize: '14px',
                                    lineHeight: '20px',
                                    color: '#f1f1f1',
                                    margin: '0 0 8px 0',
                                    wordWrap: 'break-word'
                                }}>
                                    {comment.text}
                                </p>

                                {/* Action Buttons - YouTube Style */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <button
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: '#f1f1f1',
                                            padding: '8px 12px',
                                            borderRadius: '18px',
                                            fontSize: '12px',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    >
                                        <ThumbsUp size={16} />
                                    </button>
                                    <button
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: '#f1f1f1',
                                            padding: '8px 12px',
                                            borderRadius: '18px',
                                            fontSize: '12px',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    >
                                        <ThumbsDown size={16} />
                                    </button>
                                    <button
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: '#f1f1f1',
                                            padding: '8px 12px',
                                            borderRadius: '18px',
                                            fontSize: '12px',
                                            fontWeight: '500',
                                            cursor: 'pointer',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    >
                                        Reply
                                    </button>
                                </div>
                            </div>

                            {/* More Options */}
                            <button
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#aaa',
                                    padding: '8px',
                                    borderRadius: '50%',
                                    cursor: 'pointer',
                                    width: '36px',
                                    height: '36px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'background 0.2s',
                                    flexShrink: 0
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            >
                                <MoreVertical size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
