'use client';

import React, { useState, useEffect } from 'react';
import { api, DailySentiment, Insight, FeedItem, Movie, NewsArticle, RedditPost, YouTubeVideo } from '@/services/api';
import dynamic from 'next/dynamic';

const SentimentChart = dynamic(() => import('@/components/SentimentChart').then(mod => mod.SentimentChart), { ssr: false });
const AspectRadar = dynamic(() => import('@/components/AspectRadar').then(mod => mod.AspectRadar), { ssr: false });
import { InsightCard } from '@/components/InsightCard';
import { InfiniteVisualizationFeed } from '@/components/InfiniteVisualizationFeed';
import { RedditDiscussions } from '@/components/RedditDiscussions';
import DiscussionSection from '@/components/DiscussionSection';
import { MessageSquare, Youtube, FileText, Film, ThumbsUp, Eye, Users } from 'lucide-react';
import UserRating from '@/components/UserRating';

interface Props {
    dailyData: DailySentiment[];
    insights: Insight[];
    feed: FeedItem[];
    news: NewsArticle[];
    reddit: RedditPost[];
    currentAspects: Record<string, number>;
    movie: Movie | null;
}

export const MovieDashboard: React.FC<Props> = ({ dailyData, insights, feed, news, reddit, currentAspects, movie }) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb' | 'news' | 'discussion'>('overview');
    const [youtubeVideos, setYoutubeVideos] = useState<YouTubeVideo[]>([]);
    const [expandedComments, setExpandedComments] = useState<Record<string, boolean>>({});

    useEffect(() => {
        if (activeTab === 'youtube' && movie?._id) {
            console.log("Fetching YouTube videos for:", movie._id);
            api.getMovieYoutubeVideos(movie._id)
                .then(data => {
                    console.log("Received YouTube Data:", data);
                    setYoutubeVideos(data);
                })
                .catch(err => console.error("Failed to fetch YouTube videos", err));
        }
    }, [activeTab, movie]);

    const toggleComments = (videoId: string) => {
        setExpandedComments(prev => ({ ...prev, [videoId]: !prev[videoId] }));
    };

    const getSentimentForVideo = (videoId: string) => {
        const feedItem = feed.find(f => f.source === 'youtube' && f.url.includes(videoId));
        return feedItem?.sentiment;
    };

    if (activeTab === 'youtube') {
        console.log("Render Cycle - YouTube Videos:", youtubeVideos);
    }

    return (
        <div>
            {/* TABS - Platform Sections */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
                {[
                    { key: 'overview', label: 'Overview', icon: <Film size={16} /> },
                    { key: 'news', label: 'News', icon: <FileText size={16} /> },
                    { key: 'discussion', label: 'Discussion', icon: <MessageSquare size={16} /> },
                    { key: 'reddit', label: 'Reddit', icon: <MessageSquare size={16} /> },
                    { key: 'youtube', label: 'YouTube', icon: <Youtube size={16} /> },
                    { key: 'wiki', label: 'Wiki', icon: <FileText size={16} /> },
                    { key: 'imdb', label: 'IMDB', icon: <Film size={16} /> }
                ].map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as 'overview' | 'reddit' | 'youtube' | 'wiki' | 'imdb' | 'news' | 'discussion')}
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
                <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '3rem' }}>

                    {/* Movie Details Card */}
                    {movie && (
                        <div className="card" style={{ marginBottom: '2rem' }}>
                            <h3 style={{ marginTop: 0, textAlign: 'center', marginBottom: '1.5rem' }}>Movie Details</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', fontSize: '1rem', color: '#ccc' }}>
                                <div style={{ textAlign: 'right', paddingRight: '1rem', borderRight: '1px solid #333' }}>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Director:</strong> {movie.crew?.director || 'N/A'}</p>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Writers:</strong> {movie.crew?.writers?.join(', ') || 'N/A'}</p>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Genres:</strong> {movie.genres?.join(', ') || 'N/A'}</p>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Box Office:</strong> {movie.box_office || 'N/A'}</p>
                                </div>
                                <div>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Cast:</strong> {movie.cast?.slice(0, 5).join(', ') || 'N/A'}</p>
                                    <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>IMDB:</strong> ⭐ {movie.imdb?.rating || 'N/A'}</p>
                                    {movie.rotten_tomatoes?.critics_score && (
                                        <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Rotten Tomatoes:</strong> 🍅 {movie.rotten_tomatoes.critics_score}%</p>
                                    )}
                                    {movie.metascore && (
                                        <p style={{ marginBottom: '0.8rem' }}><strong style={{ color: '#666' }}>Metascore:</strong> {movie.metascore}/100</p>
                                    )}
                                </div>
                            </div>
                            {movie.awards && movie.awards !== 'N/A' && (
                                <p style={{ marginTop: '1.5rem', fontSize: '0.9rem', color: '#999', borderTop: '1px solid #333', paddingTop: '1rem', textAlign: 'center' }}>
                                    <strong style={{ color: '#666' }}>🏆 Awards:</strong> {movie.awards}
                                </p>
                            )}
                        </div>
                    )}

                    {/* Aspect Analysis (Moved to Top) */}
                    <div className="card" style={{ marginBottom: '1rem' }}>
                        <h3 style={{ marginTop: 0, textAlign: 'center' }}>Aspect Analysis</h3>
                        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
                            {Object.keys(currentAspects).length > 0 ? (
                                <AspectRadar aspects={currentAspects} />
                            ) : (
                                <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
                                    Not enough data
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Dynamic Visualizations */}
                    {movie && (
                        <div style={{ marginBottom: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                            <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>📊 Dynamic Insights</h3>
                            <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem', maxWidth: '600px' }}>
                                AI-generated visualizations analyzing sentiment trends, platform activity, and audience engagement.
                            </p>
                            <InfiniteVisualizationFeed movieId={movie._id || movie.movie_id || ''} />
                        </div>
                    )}

                    {/* Trailers Section */}
                    {movie && movie.trailers && movie.trailers.length > 0 && (
                        <div style={{ marginBottom: '1rem' }}>
                            <h3 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', textAlign: 'center' }}>🎥 Trailers & Videos</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                                {movie.trailers.slice(0, 3).map((trailer: any, index: number) => (
                                    <div key={index} className="card">
                                        <div style={{ marginBottom: '0.75rem' }}>
                                            <h4 style={{ margin: 0, fontSize: '1rem', marginBottom: '0.25rem' }}>
                                                {trailer.name}
                                            </h4>
                                            <span style={{
                                                background: trailer.type === 'Trailer' ? '#646cff' : '#00ff9d',
                                                color: '#000',
                                                padding: '0.2rem 0.5rem',
                                                borderRadius: '6px',
                                                fontSize: '0.7rem',
                                                fontWeight: 600,
                                                textTransform: 'uppercase'
                                            }}>
                                                {trailer.type}
                                            </span>
                                        </div>
                                        <div style={{
                                            position: 'relative',
                                            paddingBottom: '56.25%',
                                            height: 0,
                                            overflow: 'hidden',
                                            borderRadius: '8px',
                                            background: '#000'
                                        }}>
                                            <iframe
                                                src={`https://www.youtube.com/embed/${trailer.key}`}
                                                title={trailer.name}
                                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                allowFullScreen
                                                style={{
                                                    position: 'absolute',
                                                    top: 0,
                                                    left: 0,
                                                    width: '100%',
                                                    height: '100%',
                                                    border: 'none'
                                                }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}



                    {/* Sentiment Trend */}
                    <div className="card" style={{ marginBottom: '1rem' }}>
                        <h3 style={{ marginTop: 0, textAlign: 'center' }}>Sentiment Trend</h3>
                        <SentimentChart data={dailyData} />
                    </div>

                    {/* AI Insight Feed */}
                    <div className="card">
                        <h3 style={{ marginTop: 0, textAlign: 'center', marginBottom: '1.5rem' }}>AI Insight Feed</h3>
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {insights.map(insight => (
                                <InsightCard key={insight._id} insight={insight} />
                            ))}
                            {insights.length === 0 && <p style={{ color: '#666', textAlign: 'center' }}>No insights generated yet.</p>}
                        </div>
                    </div>

                </div>
            )}

            {activeTab === 'discussion' && (
                <div>
                    {movie && <DiscussionSection movieId={movie._id || movie.movie_id || ''} />}
                </div>
            )}

            {activeTab === 'reddit' && (
                <RedditDiscussions posts={reddit} />
            )}

            {activeTab === 'youtube' && (
                <div style={{ display: 'grid', gap: '1.5rem' }}>

                    {/* Rich YouTube Cards */}
                    {youtubeVideos.map(video => (
                        <div key={video.video_id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                            <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'stretch' }}>
                                <div style={{ width: '280px', position: 'relative', flexShrink: 0 }}>
                                    <a href={`https://www.youtube.com/watch?v=${video.video_id}`} target="_blank" rel="noreferrer">
                                        <img
                                            src={`https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`}
                                            alt={video.title}
                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                        />
                                        <div style={{ position: 'absolute', top: 10, left: 10, background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: 4, textTransform: 'uppercase', fontSize: '0.7rem', color: '#fff' }}>
                                            {video.video_type}
                                        </div>
                                    </a>
                                </div>
                                <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                    <h4 style={{ margin: '0 0 0.5rem', fontSize: '1.1rem', lineHeight: '1.3', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <a href={`https://www.youtube.com/watch?v=${video.video_id}`} target="_blank" rel="noreferrer" style={{ color: '#fff', textDecoration: 'none', flex: 1 }}>
                                            {video.title}
                                        </a>
                                        {(() => {
                                            const sentiment = video.sentiment || getSentimentForVideo(video.video_id);
                                            if (sentiment) {
                                                return (
                                                    <span style={{
                                                        fontSize: '0.75rem',
                                                        background: sentiment.score > 0 ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255, 71, 87, 0.1)',
                                                        color: sentiment.score > 0 ? '#00ff9d' : '#ff4757',
                                                        padding: '2px 6px',
                                                        borderRadius: 4,
                                                        whiteSpace: 'nowrap',
                                                        marginLeft: '0.5rem'
                                                    }}>
                                                        {sentiment.label} ({sentiment.score.toFixed(2)})
                                                    </span>
                                                );
                                            }
                                            return null;
                                        })()}
                                    </h4>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem', padding: '0.5rem 0' }}>
                                        {video.channel_image ? (
                                            <img src={video.channel_image} alt={video.channel} style={{ width: 32, height: 32, borderRadius: '50%' }} />
                                        ) : (
                                            <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#333', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Youtube size={16} /></div>
                                        )}
                                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                                            <span style={{ color: '#eee', fontSize: '0.9rem', fontWeight: 500 }}>{video.channel}</span>
                                            {video.channel_subs && <span style={{ color: '#666', fontSize: '0.75rem' }}>{parseInt(video.channel_subs).toLocaleString()} subs</span>}
                                        </div>
                                    </div>
                                    <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #333', paddingTop: '0.8rem' }}>
                                        <div style={{ display: 'flex', gap: '1rem', color: '#888', fontSize: '0.85rem' }}>
                                            {video.stats?.views && <span>{parseInt(video.stats.views as any).toLocaleString()} views</span>}
                                            {video.stats?.likes && <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><ThumbsUp size={12} /> {parseInt(video.stats.likes as any).toLocaleString()}</span>}
                                        </div>
                                        {video.comments && video.comments.length > 0 && (
                                            <button onClick={() => toggleComments(video.video_id)} style={{ background: 'transparent', border: '1px solid #444', color: '#ccc', padding: '0.3rem', borderRadius: 4, cursor: 'pointer', fontSize: '0.8rem' }}>
                                                {expandedComments[video.video_id] ? 'Hide Comments' : 'Top Comments'}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                            {expandedComments[video.video_id] && (
                                <div style={{ background: '#111', padding: '1rem', borderTop: '1px solid #222' }}>
                                    {video.comments.map(c => (
                                        <div key={c.comment_id} style={{ marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: '1px solid #222' }}>
                                            <div dangerouslySetInnerHTML={{ __html: c.text }} style={{ color: '#ccc', fontSize: '0.9rem' }} />
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Fallback */}
                    {youtubeVideos.length === 0 && (
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {feed.filter(f => f.source === 'youtube').map(item => (
                                <div key={item._id} className="card">
                                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
                                        <Youtube size={14} /> YouTube
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

                </div>
            )}

            {activeTab === 'wiki' && (
                <div>
                    {movie?.wikipedia ? (
                        <div style={{ lineHeight: '1.6', color: '#ccc' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid #333', paddingBottom: '1rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', fontSize: '1.2rem', fontWeight: 'bold' }}>
                                    <FileText size={24} />
                                    <span>{movie.wikipedia.page_title || movie.title}</span>
                                </div>
                                {movie.wikipedia.url && (
                                    <a
                                        href={movie.wikipedia.url}
                                        target="_blank"
                                        rel="noreferrer"
                                        style={{ background: '#333', color: '#fff', padding: '0.4rem 0.8rem', borderRadius: '6px', fontSize: '0.9rem', textDecoration: 'none' }}
                                    >
                                        Read on Wikipedia
                                    </a>
                                )}
                            </div>

                            {/* Summary */}
                            {movie.wikipedia.summary && (
                                <div style={{ marginBottom: '2rem', fontSize: '1.05rem' }}>
                                    <p>{movie.wikipedia.summary}</p>
                                </div>
                            )}

                            {/* Sections */}
                            {movie.wikipedia.sections && movie.wikipedia.sections.map((section, idx) => (
                                <div key={idx} className="card" style={{ marginBottom: '1.5rem' }}>
                                    <h3 style={{ marginTop: 0, borderBottom: '1px solid #333', paddingBottom: '0.5rem', marginBottom: '1rem', color: '#fff' }}>
                                        {section.title}
                                    </h3>
                                    <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem' }}>
                                        {section.content}
                                    </div>
                                </div>
                            ))}

                            {(!movie.wikipedia.sections || movie.wikipedia.sections.length === 0) && !movie.wikipedia.summary && (
                                <p style={{ color: '#666' }}>No Wikipedia content available.</p>
                            )}
                        </div>
                    ) : (
                        /* Fallback to Feed Items if no structured data */
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
                </div>
            )}

            {activeTab === 'imdb' && (
                <div style={{ display: 'grid', gap: '2rem' }}>
                    {movie ? (
                        <>
                            {/* Top Section: Ratings & Poster */}
                            <div className="card" style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
                                {/* Poster (prefer IMDB poster, fallback to TMDB) */}
                                {(movie.poster || movie.poster_url) ? (
                                    <img
                                        src={movie.poster || movie.poster_url}
                                        alt={movie.title}
                                        style={{ width: '150px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }}
                                    />
                                ) : (
                                    <div style={{ width: '150px', height: '225px', background: '#333', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Film size={48} color="#666" />
                                    </div>
                                )}

                                <div style={{ flex: 1 }}>
                                    <div className="flex justify-between items-start">
                                        <h2 style={{ marginTop: 0, marginBottom: '0.5rem' }}>
                                            {movie.title} {(movie.year || (movie.release_date && `(${new Date(movie.release_date).getFullYear()})`))}
                                        </h2>
                                        <UserRating movieId={movie._id || movie.movie_id || ''} />
                                    </div>
                                    {movie.tagline && <p style={{ fontStyle: 'italic', color: '#999', marginBottom: '1.5rem' }}>"{movie.tagline}"</p>}
                                    {movie.rated && (
                                        <div style={{ display: 'inline-block', background: '#333', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem', marginBottom: '1rem' }}>
                                            Rated: {movie.rated}
                                        </div>
                                    )}

                                    {/* Ratings Grid */}
                                    <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                                        {/* IMDb - use flat field with fallback to nested */}
                                        <div style={{ textAlign: 'center' }}>
                                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f5c518' }}>
                                                {movie.imdb_rating || movie.imdb?.rating || 'N/A'}<span style={{ fontSize: '0.8rem', color: '#666' }}>/10</span>
                                            </div>
                                            <div style={{ fontSize: '0.8rem', color: '#666' }}>IMDb</div>
                                            {(movie.imdb_votes || movie.imdb?.votes) && (
                                                <div style={{ fontSize: '0.7rem', color: '#555', marginTop: '0.25rem' }}>
                                                    {(movie.imdb_votes || movie.imdb?.votes)?.toLocaleString()} votes
                                                </div>
                                            )}
                                        </div>
                                        {/* Rotten Tomatoes */}
                                        {movie.rotten_tomatoes?.critics_score && (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: movie.rotten_tomatoes.critics_score >= 60 ? '#ff4757' : '#00ff9d' }}>
                                                    {movie.rotten_tomatoes.critics_score}%
                                                </div>
                                                <div style={{ fontSize: '0.8rem', color: '#666' }}>Tomatometer</div>
                                            </div>
                                        )}
                                        {/* Metascore */}
                                        {movie.metascore && (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{
                                                    width: '40px', height: '40px', lineHeight: '40px',
                                                    background: movie.metascore >= 60 ? '#66cc33' : '#ffcc33',
                                                    color: '#fff', fontWeight: 'bold', borderRadius: '4px', margin: '0 auto'
                                                }}>
                                                    {movie.metascore}
                                                </div>
                                                <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '5px' }}>Metascore</div>
                                            </div>
                                        )}
                                        {/* TMDB Vote */}
                                        {movie.vote_average && (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#01d277' }}>
                                                    {movie.vote_average.toFixed(1)}
                                                </div>
                                                <div style={{ fontSize: '0.8rem', color: '#666' }}>TMDB</div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Quick Stats */}
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '1rem', fontSize: '0.9rem' }}>
                                        <div><strong style={{ color: '#666' }}>Runtime:</strong> {movie.runtime || (movie.runtime_minutes && `${movie.runtime_minutes} min`) || 'N/A'}</div>
                                        <div><strong style={{ color: '#666' }}>Genre:</strong> {Array.isArray(movie.genre) ? movie.genre.join(', ') : movie.genre || movie.genres?.join(', ') || 'N/A'}</div>
                                        <div><strong style={{ color: '#666' }}>Budget:</strong> {movie.budget ? `$${(movie.budget / 1000000).toFixed(1)}M` : 'N/A'}</div>
                                        <div><strong style={{ color: '#666' }}>Revenue:</strong> {movie.revenue ? `$${(movie.revenue / 1000000).toFixed(1)}M` : 'N/A'}</div>
                                        <div><strong style={{ color: '#666' }}>Box Office:</strong> {movie.box_office || 'N/A'}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Overview/Plot Section */}
                            <div className="card">
                                <h3>Plot Overview</h3>
                                <p style={{ lineHeight: '1.6', color: '#ddd' }}>{movie.plot || movie.overview || 'No overview available.'}</p>
                            </div>

                            {/* Cast & Crew Section */}
                            <div className="card">
                                <h3>Cast & Crew</h3>
                                <div style={{ marginBottom: '1rem' }}>
                                    <strong style={{ color: '#666' }}>Director:</strong> {movie.director || movie.crew?.director || 'N/A'}
                                </div>
                                <div style={{ marginBottom: '1rem' }}>
                                    <strong style={{ color: '#666' }}>Writers:</strong> {movie.crew?.writers?.join(', ') || 'N/A'}
                                </div>
                                <div>
                                    <strong style={{ color: '#666' }}>Cast:</strong>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                                        {(() => {
                                            const castList = movie.cast || (typeof movie.actors === 'string' ? movie.actors.split(', ') : movie.actors);
                                            return castList && castList.length > 0 ? castList.slice(0, 10).map((actor: string, idx: number) => (
                                                <span key={idx} style={{ background: '#1c1c21', padding: '0.3rem 0.8rem', borderRadius: '20px', fontSize: '0.9rem', border: '1px solid #333' }}>
                                                    {actor}
                                                </span>
                                            )) : 'N/A';
                                        })()}
                                    </div>
                                </div>
                            </div>

                            {/* Production Info */}
                            {movie.production_companies && movie.production_companies.length > 0 && (
                                <div className="card">
                                    <h3>Production</h3>
                                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                                        {movie.production_companies.map((company, idx) => (
                                            <span key={idx} style={{ color: '#aaa' }}>{company}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <p style={{ color: '#666' }}>Movie data not available.</p>
                    )}

                    {/* Fallback to Feed Items if any exist (e.g. plot from OMDB stored as feed item) */}
                    {feed.filter(f => f.source === 'imdb').length > 0 && (
                        <div style={{ borderTop: '1px solid #333', paddingTop: '1rem' }}>
                            <h4 style={{ color: '#666' }}>Additional Notes</h4>
                            {feed.filter(f => f.source === 'imdb').map(item => (
                                <div key={item._id} className="card" style={{ marginBottom: '1rem' }}>
                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>{item.text}</p>
                                </div>
                            ))}
                        </div>
                    )}
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
                                            <span>{new Date(article.published_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
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
