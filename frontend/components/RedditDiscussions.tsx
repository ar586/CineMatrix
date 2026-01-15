'use client';

import { RedditPost } from '@/services/api';
import { MessageSquare, ThumbsUp, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface RedditDiscussionsProps {
    posts: RedditPost[];
}

export function RedditDiscussions({ posts }: RedditDiscussionsProps) {
    const [expandedPosts, setExpandedPosts] = useState<Set<string>>(new Set());

    const togglePost = (postId: string) => {
        const newExpanded = new Set(expandedPosts);
        if (newExpanded.has(postId)) {
            newExpanded.delete(postId);
        } else {
            newExpanded.add(postId);
        }
        setExpandedPosts(newExpanded);
    };

    if (!posts || posts.length === 0) {
        return (
            <div style={{
                padding: '3rem',
                textAlign: 'center',
                color: '#666',
                background: 'var(--bg-card)',
                borderRadius: '12px',
                border: '1px solid var(--border-subtle)'
            }}>
                <MessageSquare size={48} style={{ margin: '0 auto 1rem', opacity: 0.3 }} />
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#888' }}>No Reddit Discussions Found</h3>
                <p style={{ margin: 0, fontSize: '0.9rem' }}>
                    There are no Reddit posts available for this movie yet.
                </p>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {posts.map((post) => {
                const isExpanded = expandedPosts.has(post._id);
                const hasComments = post.comments && post.comments.length > 0;
                const truncatedText = post.selftext && post.selftext.length > 300
                    ? post.selftext.substring(0, 300) + '...'
                    : post.selftext;

                return (
                    <div
                        key={post._id}
                        style={{
                            background: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: '12px',
                            padding: '1.5rem',
                            transition: 'all 0.2s ease'
                        }}
                        className="card"
                    >
                        {/* Post Header */}
                        <div style={{ marginBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                <span style={{
                                    background: '#ff4500',
                                    color: 'white',
                                    padding: '0.2rem 0.6rem',
                                    borderRadius: '12px',
                                    fontSize: '0.75rem',
                                    fontWeight: 'bold'
                                }}>
                                    r/{post.subreddit}
                                </span>
                                <span style={{ color: '#666', fontSize: '0.85rem' }}>
                                    {new Date(post.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                                </span>
                            </div>

                            <a
                                href={post.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    fontSize: '1.3rem',
                                    fontWeight: 'bold',
                                    color: 'var(--text-main)',
                                    textDecoration: 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    marginBottom: '0.5rem'
                                }}
                            >
                                {post.title}
                                <ExternalLink size={18} style={{ color: '#646cff', flexShrink: 0 }} />
                            </a>

                            <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', color: '#888', fontSize: '0.9rem' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <ThumbsUp size={16} />
                                    {post.score} upvotes
                                </span>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <MessageSquare size={16} />
                                    {post.num_comments} comments
                                </span>
                            </div>
                        </div>

                        {/* Post Body */}
                        {post.selftext && (
                            <div style={{
                                color: '#ccc',
                                lineHeight: '1.6',
                                marginBottom: '1rem',
                                padding: '1rem',
                                background: 'rgba(255, 255, 255, 0.02)',
                                borderRadius: '8px',
                                borderLeft: '3px solid #646cff'
                            }}>
                                {truncatedText}
                            </div>
                        )}

                        {/* Comments Section */}
                        {hasComments && (
                            <>
                                <button
                                    onClick={() => togglePost(post._id)}
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        background: 'rgba(100, 108, 255, 0.1)',
                                        border: '1px solid rgba(100, 108, 255, 0.3)',
                                        borderRadius: '8px',
                                        color: '#646cff',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '0.5rem',
                                        fontSize: '0.9rem',
                                        fontWeight: '500',
                                        transition: 'all 0.2s ease'
                                    }}
                                >
                                    {isExpanded ? (
                                        <>
                                            <ChevronUp size={18} />
                                            Hide Top Comments
                                        </>
                                    ) : (
                                        <>
                                            <ChevronDown size={18} />
                                            Show Top {post.comments.length} Comments
                                        </>
                                    )}
                                </button>

                                {isExpanded && (
                                    <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {post.comments.map((comment) => (
                                            <div
                                                key={comment.comment_id}
                                                style={{
                                                    padding: '1rem',
                                                    background: 'rgba(255, 255, 255, 0.03)',
                                                    borderRadius: '8px',
                                                    borderLeft: '2px solid #00ff9d'
                                                }}
                                            >
                                                <div style={{
                                                    color: '#ddd',
                                                    lineHeight: '1.5',
                                                    marginBottom: '0.5rem'
                                                }}>
                                                    {comment.text}
                                                </div>
                                                <div style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    gap: '0.3rem',
                                                    color: '#00ff9d',
                                                    fontSize: '0.85rem',
                                                    fontWeight: '500'
                                                }}>
                                                    <ThumbsUp size={14} />
                                                    {comment.score}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
