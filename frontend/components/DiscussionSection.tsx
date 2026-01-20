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
    likes: number;
    dislikes: number;
    liked_by: string[];
    disliked_by: string[];
    parent_id?: string;
    replies: string[];
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
    const [replyingTo, setReplyingTo] = useState<string | null>(null);
    const [replyText, setReplyText] = useState('');
    const [expandedReplies, setExpandedReplies] = useState<Record<string, Comment[]>>({});
    const [loadingReplies, setLoadingReplies] = useState<Record<string, boolean>>({});

    useEffect(() => {
        fetchComments();
    }, [movieId]);

    const fetchComments = async () => {
        try {
            const res = await fetch(`/api/movies/${movieId}/comments/`);
            if (res.ok) {
                const data = await res.json();
                // Only show top-level comments (no parent_id)
                setComments(data.filter((c: Comment) => c.text && c.text.trim().length > 0 && !c.parent_id));
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
            const res = await fetch(`/api/movies/${movieId}/comments/`, {
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

    const handleLike = async (commentId: string) => {
        if (!token) return;

        try {
            const res = await fetch(`/api/movies/${movieId}/comments/${commentId}/like`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                const updatedComment = await res.json();
                setComments(comments.map(c => c._id === commentId ? updatedComment : c));
            }
        } catch (err) {
            console.error("Failed to like comment", err);
        }
    };

    const handleDislike = async (commentId: string) => {
        if (!token) return;

        try {
            const res = await fetch(`/api/movies/${movieId}/comments/${commentId}/dislike`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                const updatedComment = await res.json();
                setComments(comments.map(c => c._id === commentId ? updatedComment : c));
            }
        } catch (err) {
            console.error("Failed to dislike comment", err);
        }
    };

    const handleReplySubmit = async (parentId: string) => {
        if (!token || !replyText.trim()) return;

        try {
            const res = await fetch(`/api/movies/${movieId}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    text: replyText,
                    parent_id: parentId
                })
            });

            if (res.ok) {
                setReplyText('');
                setReplyingTo(null);
                // Refresh comments to show the new reply count
                fetchComments();
                // If replies are expanded, refresh them too
                if (expandedReplies[parentId]) {
                    fetchReplies(parentId);
                }
            }
        } catch (err) {
            console.error("Failed to post reply", err);
        }
    };

    const fetchReplies = async (commentId: string) => {
        // Toggle - if already expanded, collapse
        if (expandedReplies[commentId]) {
            const newExpanded = { ...expandedReplies };
            delete newExpanded[commentId];
            setExpandedReplies(newExpanded);
            return;
        }

        // Fetch replies
        setLoadingReplies({ ...loadingReplies, [commentId]: true });
        try {
            const res = await fetch(`/api/movies/${movieId}/comments/${commentId}/replies`);
            if (res.ok) {
                const replies = await res.json();
                setExpandedReplies({ ...expandedReplies, [commentId]: replies });
            }
        } catch (err) {
            console.error("Failed to fetch replies", err);
        } finally {
            setLoadingReplies({ ...loadingReplies, [commentId]: false });
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
                    {comments.map((comment) => {
                        const userLiked = user && comment.liked_by.includes(user.username);
                        const userDisliked = user && comment.disliked_by.includes(user.username);

                        return (
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
                                            onClick={() => user && handleLike(comment._id)}
                                            disabled={!user}
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: userLiked ? '#3ea6ff' : '#f1f1f1',
                                                padding: '8px 12px',
                                                borderRadius: '18px',
                                                fontSize: '12px',
                                                cursor: user ? 'pointer' : 'not-allowed',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                transition: 'background 0.2s',
                                                opacity: !user ? 0.5 : 1
                                            }}
                                            onMouseEnter={(e) => user && (e.currentTarget.style.background = '#272727')}
                                            onMouseLeave={(e) => user && (e.currentTarget.style.background = 'transparent')}
                                        >
                                            <ThumbsUp size={16} fill={userLiked ? '#3ea6ff' : 'none'} />
                                            {comment.likes > 0 && <span>{comment.likes}</span>}
                                        </button>
                                        <button
                                            onClick={() => user && handleDislike(comment._id)}
                                            disabled={!user}
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: userDisliked ? '#3ea6ff' : '#f1f1f1',
                                                padding: '8px 12px',
                                                borderRadius: '18px',
                                                fontSize: '12px',
                                                cursor: user ? 'pointer' : 'not-allowed',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                transition: 'background 0.2s',
                                                opacity: !user ? 0.5 : 1
                                            }}
                                            onMouseEnter={(e) => user && (e.currentTarget.style.background = '#272727')}
                                            onMouseLeave={(e) => user && (e.currentTarget.style.background = 'transparent')}
                                        >
                                            <ThumbsDown size={16} fill={userDisliked ? '#3ea6ff' : 'none'} />
                                        </button>
                                        <button
                                            onClick={() => user && setReplyingTo(replyingTo === comment._id ? null : comment._id)}
                                            disabled={!user}
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: '#f1f1f1',
                                                padding: '8px 12px',
                                                borderRadius: '18px',
                                                fontSize: '12px',
                                                fontWeight: '500',
                                                cursor: user ? 'pointer' : 'not-allowed',
                                                transition: 'background 0.2s',
                                                opacity: !user ? 0.5 : 1
                                            }}
                                            onMouseEnter={(e) => user && (e.currentTarget.style.background = '#272727')}
                                            onMouseLeave={(e) => user && (e.currentTarget.style.background = 'transparent')}
                                        >
                                            Reply
                                        </button>
                                        {comment.replies.length > 0 && (
                                            <button
                                                onClick={() => fetchReplies(comment._id)}
                                                style={{
                                                    background: 'transparent',
                                                    border: 'none',
                                                    fontSize: '12px',
                                                    color: '#3ea6ff',
                                                    marginLeft: '8px',
                                                    cursor: 'pointer',
                                                    fontWeight: '500',
                                                    padding: '8px 12px',
                                                    borderRadius: '18px',
                                                    transition: 'background 0.2s'
                                                }}
                                                onMouseEnter={(e) => e.currentTarget.style.background = '#272727'}
                                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                            >
                                                {loadingReplies[comment._id] ? 'Loading...' :
                                                    expandedReplies[comment._id] ? '▼ Hide replies' :
                                                        `▶ ${comment.replies.length} ${comment.replies.length === 1 ? 'reply' : 'replies'}`}
                                            </button>
                                        )}
                                    </div>

                                    {/* Reply Input */}
                                    {replyingTo === comment._id && (
                                        <div style={{ marginTop: '12px', display: 'flex', gap: '12px' }}>
                                            <div style={{
                                                width: '32px',
                                                height: '32px',
                                                borderRadius: '50%',
                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                color: '#fff',
                                                fontSize: '14px',
                                                fontWeight: '500',
                                                flexShrink: 0
                                            }}>
                                                {user?.username.charAt(0).toUpperCase()}
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <input
                                                    type="text"
                                                    value={replyText}
                                                    onChange={(e) => setReplyText(e.target.value)}
                                                    placeholder={`Reply to @${comment.username}...`}
                                                    style={{
                                                        width: '100%',
                                                        background: 'transparent',
                                                        border: 'none',
                                                        borderBottom: '1px solid #303030',
                                                        color: '#f1f1f1',
                                                        fontSize: '13px',
                                                        padding: '6px 0',
                                                        outline: 'none'
                                                    }}
                                                    onFocus={(e) => e.target.style.borderBottomColor = '#aaa'}
                                                    onBlur={(e) => e.target.style.borderBottomColor = '#303030'}
                                                />
                                                {replyText.trim() && (
                                                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                                                        <button
                                                            onClick={() => { setReplyingTo(null); setReplyText(''); }}
                                                            style={{
                                                                background: 'transparent',
                                                                border: 'none',
                                                                color: '#aaa',
                                                                padding: '8px 14px',
                                                                borderRadius: '18px',
                                                                fontSize: '13px',
                                                                fontWeight: '500',
                                                                cursor: 'pointer'
                                                            }}
                                                        >
                                                            Cancel
                                                        </button>
                                                        <button
                                                            onClick={() => handleReplySubmit(comment._id)}
                                                            style={{
                                                                background: '#3ea6ff',
                                                                border: 'none',
                                                                color: '#0f0f0f',
                                                                padding: '8px 14px',
                                                                borderRadius: '18px',
                                                                fontSize: '13px',
                                                                fontWeight: '500',
                                                                cursor: 'pointer'
                                                            }}
                                                        >
                                                            Reply
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    {/* Nested Replies */}
                                    {expandedReplies[comment._id] && (
                                        <div style={{ marginTop: '16px', marginLeft: '56px', borderLeft: '2px solid #303030', paddingLeft: '16px' }}>
                                            {expandedReplies[comment._id].map((reply) => {
                                                const userLikedReply = user && reply.liked_by.includes(user.username);
                                                const userDislikedReply = user && reply.disliked_by.includes(user.username);

                                                return (
                                                    <div key={reply._id} style={{ marginBottom: '16px' }}>
                                                        <div style={{ display: 'flex', gap: '12px' }}>
                                                            {/* Reply Avatar */}
                                                            <div style={{
                                                                width: '32px',
                                                                height: '32px',
                                                                borderRadius: '50%',
                                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                color: '#fff',
                                                                fontSize: '14px',
                                                                fontWeight: '500',
                                                                flexShrink: 0
                                                            }}>
                                                                {reply.username.charAt(0).toUpperCase()}
                                                            </div>

                                                            <div style={{ flex: 1 }}>
                                                                {/* Reply Username and Time */}
                                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                                                    <span style={{ fontSize: '12px', fontWeight: '500', color: '#f1f1f1' }}>
                                                                        @{reply.username}
                                                                    </span>
                                                                    <span style={{ fontSize: '11px', color: '#aaa' }}>
                                                                        {timeAgo(reply.created_at)}
                                                                    </span>
                                                                </div>

                                                                {/* Reply Text */}
                                                                <p style={{
                                                                    fontSize: '13px',
                                                                    lineHeight: '18px',
                                                                    color: '#f1f1f1',
                                                                    margin: '0 0 6px 0',
                                                                    wordWrap: 'break-word'
                                                                }}>
                                                                    {reply.text}
                                                                </p>

                                                                {/* Reply Action Buttons */}
                                                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                                    <button
                                                                        onClick={() => user && handleLike(reply._id)}
                                                                        disabled={!user}
                                                                        style={{
                                                                            background: 'transparent',
                                                                            border: 'none',
                                                                            color: userLikedReply ? '#3ea6ff' : '#f1f1f1',
                                                                            padding: '6px 10px',
                                                                            borderRadius: '18px',
                                                                            fontSize: '11px',
                                                                            cursor: user ? 'pointer' : 'not-allowed',
                                                                            display: 'flex',
                                                                            alignItems: 'center',
                                                                            gap: '4px',
                                                                            opacity: !user ? 0.5 : 1
                                                                        }}
                                                                    >
                                                                        <ThumbsUp size={14} fill={userLikedReply ? '#3ea6ff' : 'none'} />
                                                                        {reply.likes > 0 && <span>{reply.likes}</span>}
                                                                    </button>
                                                                    <button
                                                                        onClick={() => user && handleDislike(reply._id)}
                                                                        disabled={!user}
                                                                        style={{
                                                                            background: 'transparent',
                                                                            border: 'none',
                                                                            color: userDislikedReply ? '#3ea6ff' : '#f1f1f1',
                                                                            padding: '6px 10px',
                                                                            borderRadius: '18px',
                                                                            fontSize: '11px',
                                                                            cursor: user ? 'pointer' : 'not-allowed',
                                                                            display: 'flex',
                                                                            alignItems: 'center',
                                                                            gap: '4px',
                                                                            opacity: !user ? 0.5 : 1
                                                                        }}
                                                                    >
                                                                        <ThumbsDown size={14} fill={userDislikedReply ? '#3ea6ff' : 'none'} />
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
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
                        );
                    })}
                </div>
            )}
        </div>
    );
}
