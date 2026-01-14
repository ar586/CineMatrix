'use client';

import React, { useState } from 'react';
import type { DailySentiment, Insight, FeedItem, Movie, NewsArticle } from '@/services/api';
import { SentimentChart } from '@/components/SentimentChart';
import { AspectRadar } from '@/components/AspectRadar';
import { InsightCard } from '@/components/InsightCard';
import { MessageSquare, Youtube, FileText, Film } from 'lucide-react';

interface Props {
    dailyData: DailySentiment[];
    insights: Insight[];
    feed: FeedItem[];
    news: NewsArticle[];
    currentAspects: Record<string, number>;
    movie: Movie | null;
}

export const MovieDashboard: React.FC<Props> = ({ dailyData, insights, feed, news, currentAspects, movie }) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb' | 'news'>('overview');

    return (
        <div>
            {/* TABS - Platform Sections */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
                {[
                    { key: 'overview', label: 'Overview', icon: <Film size={16} /> },
                    { key: 'news', label: 'News', icon: <FileText size={16} /> },
                    { key: 'reddit', label: 'Reddit', icon: <MessageSquare size={16} /> },
                    { key: 'youtube', label: 'YouTube', icon: <Youtube size={16} /> },
                    { key: 'wiki', label: 'Wiki', icon: <FileText size={16} /> },
                    { key: 'imdb', label: 'IMDB', icon: <Film size={16} /> }
                ].map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as 'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb' | 'news')}
                        style={{
                            background: activeTab === tab.key ? '#1c1c21' : 'transparent',
                            color: activeTab === tab.key ? '#fff' : '#666',
                            border: activeTab === tab.key ? '1px solid #27272a' : 'none',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* CONTENT */}
            {activeTab === 'overview' && (
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                    <div className="left-col">
                        {/* Metadata Card */}
                        {movie && (
                            <div className="card" style={{ marginBottom: '2rem' }}>
                                <h3 style={{ marginTop: 0 }}>Movie Details</h3>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem', color: '#ccc' }}>
                                    <div>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Director:</strong> {movie.crew?.director || 'N/A'}</p>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Writers:</strong> {movie.crew?.writers?.join(', ') || 'N/A'}</p>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Genres:</strong> {movie.genres?.join(', ') || 'N/A'}</p>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Box Office:</strong> {movie.box_office || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Cast:</strong> {movie.cast?.slice(0, 5).join(', ') || 'N/A'}</p>
                                        <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>IMDB:</strong> ⭐ {movie.imdb?.rating || 'N/A'}</p>
                                        {movie.rotten_tomatoes?.critics_score && (
                                            <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Rotten Tomatoes:</strong> 🍅 {movie.rotten_tomatoes.critics_score}%</p>
                                        )}
                                        {movie.metascore && (
                                            <p style={{ marginBottom: '0.5rem' }}><strong style={{ color: '#666' }}>Metascore:</strong> {movie.metascore}/100</p>
                                        )}
                                    </div>
                                </div>
                                {movie.awards && movie.awards !== 'N/A' && (
                                    <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#999', borderTop: '1px solid #333', paddingTop: '0.5rem' }}>
                                        <strong style={{ color: '#666' }}>🏆 Awards:</strong> {movie.awards}
                                    </p>
                                )}
                            </div>
                        )}

                        <div className="card" style={{ marginBottom: '2rem' }}>
                            <h3 style={{ marginTop: 0 }}>Sentiment Trend</h3>
                            <SentimentChart data={dailyData} />
                        </div>

                        <div className="card">
                            <h3 style={{ marginTop: 0 }}>AI Insight Feed</h3>
                            {insights.map(insight => (
                                <InsightCard key={insight._id} insight={insight} />
                            ))}
                            {insights.length === 0 && <p style={{ color: '#666' }}>No insights generated yet.</p>}
                        </div>
                    </div>

                    <div className="right-col">
                        <div className="card" style={{ marginBottom: '2rem' }}>
                            <h3 style={{ marginTop: 0 }}>Aspect Analysis</h3>
                            {Object.keys(currentAspects).length > 0 ? (
                                <AspectRadar aspects={currentAspects} />
                            ) : (
                                <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
                                    Not enough data
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'reddit' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {feed.filter(f => f.source === 'reddit').map(item => (
                        <div key={item._id} className="card">
                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
                                <MessageSquare size={14} /> Reddit • {new Date(item.created_at).toLocaleDateString()}
                            </div>
                            <p style={{ margin: '0 0 0.5rem', fontSize: '1rem' }}>{item.text}</p>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                <a href={item.url} target="_blank" rel="noreferrer" style={{ color: '#646cff' }}>View Post</a>
                                <span style={{ color: item.sentiment.score > 0 ? '#00ff9d' : '#ff4757' }}>
                                    {item.sentiment.label} ({item.sentiment.score})
                                </span>
                            </div>
                        </div>
                    ))}
                    {feed.filter(f => f.source === 'reddit').length === 0 && <p>No Reddit data found.</p>}
                </div>
            )}

            {activeTab === 'youtube' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {feed.filter(f => f.source === 'youtube').map(item => (
                        <div key={item._id} className="card">
                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
                                <Youtube size={14} /> YouTube • {new Date(item.created_at).toLocaleDateString()}
                            </div>
                            <p style={{ margin: '0 0 0.5rem', fontSize: '1rem' }}>{item.text}</p>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                <a href={item.url} target="_blank" rel="noreferrer" style={{ color: '#646cff' }}>Watch Video</a>
                                <span style={{ color: item.sentiment.score > 0 ? '#00ff9d' : '#ff4757' }}>
                                    {item.sentiment.label} ({item.sentiment.score})
                                </span>
                            </div>
                        </div>
                    ))}
                    {feed.filter(f => f.source === 'youtube').length === 0 && <p>No YouTube data found.</p>}
                </div>
            )}

            {activeTab === 'wiki' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {feed.filter(f => f.source === 'wikipedia').map(item => (
                        <div key={item._id} className="card">
                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
                                <FileText size={14} /> Wikipedia
                            </div>
                            <p style={{ margin: '0 0 0.5rem', fontSize: '1rem' }}>{item.text}</p>
                            <a href={item.url} target="_blank" rel="noreferrer" style={{ color: '#646cff', fontSize: '0.8rem' }}>Read More</a>
                        </div>
                    ))}
                    {feed.filter(f => f.source === 'wikipedia').length === 0 && <p>No Wikipedia data found.</p>}
                </div>
            )}

            {activeTab === 'imdb' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {feed.filter(f => f.source === 'imdb').map(item => (
                        <div key={item._id} className="card">
                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
                                <Film size={14} /> IMDB
                            </div>
                            <p style={{ margin: '0 0 0.5rem', fontSize: '1rem' }}>{item.text}</p>
                            <a href={item.url} target="_blank" rel="noreferrer" style={{ color: '#646cff', fontSize: '0.8rem' }}>View on IMDB</a>
                        </div>
                    ))}
                    {feed.filter(f => f.source === 'imdb').length === 0 && <p>No IMDB data found.</p>}
                </div>
            )}

            {activeTab === 'news' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {news.map(article => {
                        // Category badge color
                        const categoryColors: Record<string, string> = {
                            box_office: '#00ff9d',
                            controversy: '#ff4757',
                            awards: '#f5c518',
                            production: '#646cff',
                            reviews: '#a1a1aa',
                            cast_news: '#ff6b9d',
                            general: '#666'
                        };

                        // Sentiment color
                        const sentimentColor = article.sentiment === 'positive' ? '#00ff9d' :
                            article.sentiment === 'negative' ? '#ff4757' : '#a1a1aa';

                        return (
                            <div key={article._id} className="card">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.75rem' }}>
                                    <div style={{ flex: 1 }}>
                                        <a href={article.url} target="_blank" rel="noreferrer" style={{ color: '#fff', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600 }}>
                                            {article.title}
                                        </a>
                                        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', fontSize: '0.8rem', color: '#666' }}>
                                            <span>{article.source}</span>
                                            <span>•</span>
                                            <span>{new Date(article.published_date).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                        <span style={{
                                            background: categoryColors[article.category] || '#666',
                                            color: '#000',
                                            padding: '0.2rem 0.6rem',
                                            borderRadius: '12px',
                                            fontSize: '0.7rem',
                                            fontWeight: 600,
                                            textTransform: 'uppercase'
                                        }}>
                                            {article.category.replace('_', ' ')}
                                        </span>
                                    </div>
                                </div>

                                {article.insights.length > 0 && (
                                    <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid #27272a' }}>
                                        <p style={{ fontSize: '0.85rem', color: '#999', marginBottom: '0.5rem', fontWeight: 600 }}>Key Insights:</p>
                                        <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.9rem', color: '#ccc' }}>
                                            {article.insights.map((insight, idx) => (
                                                <li key={idx} style={{ marginBottom: '0.3rem' }}>{insight}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', fontSize: '0.8rem' }}>
                                    <span style={{ color: sentimentColor, fontWeight: 600 }}>
                                        {article.sentiment.toUpperCase()}
                                    </span>
                                    <span style={{ color: '#666' }}>
                                        Relevance: {(article.relevance_score * 100).toFixed(0)}%
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                    {news.length === 0 && <p>No news articles found. Run the pipeline to fetch news.</p>}
                </div>
            )}
        </div>
    );
};
