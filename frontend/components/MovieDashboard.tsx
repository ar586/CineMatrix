'use client';

import React, { useState } from 'react';
import type { DailySentiment, Insight, FeedItem } from '@/services/api';
import { SentimentChart } from '@/components/SentimentChart';
import { AspectRadar } from '@/components/AspectRadar';
import { InsightCard } from '@/components/InsightCard';
import { MessageSquare, Youtube, FileText, Film } from 'lucide-react';

interface Props {
    dailyData: DailySentiment[];
    insights: Insight[];
    feed: FeedItem[];
    currentAspects: Record<string, number>;
}

export const MovieDashboard: React.FC<Props> = ({ dailyData, insights, feed, currentAspects }) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb'>('overview');

    return (
        <div>
            {/* TABS - Platform Sections */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
                {[
                    { key: 'overview', label: 'Overview', icon: <Film size={16} /> },
                    { key: 'reddit', label: 'Reddit', icon: <MessageSquare size={16} /> },
                    { key: 'youtube', label: 'YouTube', icon: <Youtube size={16} /> },
                    { key: 'wiki', label: 'Wiki', icon: <FileText size={16} /> },
                    { key: 'imdb', label: 'IMDB', icon: <Film size={16} /> }
                ].map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as 'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb')}
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
        </div>
    );
};
