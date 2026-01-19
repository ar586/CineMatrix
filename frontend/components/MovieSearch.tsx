'use client';

import { useState } from 'react';
import type { Movie } from '@/services/api';
import Link from 'next/link';
import { Search, Flame, TrendingUp } from 'lucide-react';

export default function MovieSearch({ initialMovies }: { initialMovies: Movie[] }) {
    const [searchQuery, setSearchQuery] = useState('');

    // Helper to get total volume
    const getVolume = (v: number | { reddit_posts: number; youtube_videos: number } | undefined) => {
        if (!v) return 0;
        if (typeof v === 'number') return v;
        return (v.reddit_posts || 0) + (v.youtube_videos || 0);
    };

    const getHeatScore = (movie: Movie) => {
        const vol = getVolume(movie.daily_sentiment_summary?.volume);
        return (movie.daily_sentiment_summary?.volatility || 0) * 10 + vol;
    };

    // Filter movies based on search
    const filteredMovies = initialMovies.filter(movie =>
        movie.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Categorize filtered movies
    const latestReleases = filteredMovies.filter(movie => {
        if (!movie.release_date) return false;
        const year = new Date(movie.release_date).getFullYear();
        return year >= 2025;
    }).sort((a, b) => new Date(b.release_date!).getTime() - new Date(a.release_date!).getTime());

    const modernClassics = filteredMovies.filter(movie => {
        if (!movie.release_date) return true; // Fallback
        const year = new Date(movie.release_date).getFullYear();
        return year < 2025;
    }).sort((a, b) => getHeatScore(b) - getHeatScore(a));

    // Jumbotron Logic: Top 3 Latest, fill with hottest if needed
    let jumbotronMovies: Movie[] = [];
    if (!searchQuery) {
        jumbotronMovies = [...latestReleases.slice(0, 3)];
        if (jumbotronMovies.length < 3) {
            const remaining = 3 - jumbotronMovies.length;
            const fillMovies = modernClassics
                .filter(m => !jumbotronMovies.find(jm => jm.movie_id === m.movie_id))
                .slice(0, remaining);
            jumbotronMovies = [...jumbotronMovies, ...fillMovies];
        }
    }

    return (
        <div>
            {/* JUMBOTRON CONTAINER (Always Consistent) */}
            <div
                style={{
                    marginBottom: '4rem',
                    padding: '4rem 2rem',
                    background: 'radial-gradient(circle at top right, #1c1c21 0%, #0a0a0c 100%)',
                    borderRadius: '32px',
                    border: '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    position: 'relative',
                    overflow: 'hidden',
                    minHeight: searchQuery ? 'auto' : '600px', // Allow shrink when searching
                    transition: 'all 0.3s ease'
                }}
            >
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '1px',
                    background: 'linear-gradient(90deg, transparent, rgba(100, 108, 255, 0.3), transparent)'
                }} />

                {/* SEARCH BAR: Absolute Top-Left inside Jumbotron */}
                <div style={{
                    position: 'absolute',
                    top: '2rem',
                    left: '2rem',
                    width: '300px',
                    zIndex: 50
                }}>
                    <div style={{
                        position: 'absolute',
                        left: '1rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        display: 'flex',
                        alignItems: 'center',
                        pointerEvents: 'none'
                    }}>
                        <Search size={16} color="#aaa" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                            background: 'rgba(0, 0, 0, 0.3)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            color: '#fff',
                            fontSize: '0.95rem',
                            backdropFilter: 'blur(8px)',
                            outline: 'none',
                            transition: 'all 0.2s'
                        }}
                        onFocus={(e) => {
                            e.currentTarget.style.borderColor = '#646cff';
                            e.currentTarget.style.background = 'rgba(0, 0, 0, 0.6)';
                        }}
                        onBlur={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                            e.currentTarget.style.background = 'rgba(0, 0, 0, 0.3)';
                        }}
                    />
                </div>

                {/* HEADER BRANDING (Always visible for context) */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: searchQuery ? '1rem' : '1.5rem' }}>
                    <Flame size={searchQuery ? 40 : 56} color="#646cff" style={{ filter: 'drop-shadow(0 0 10px rgba(100, 108, 255, 0.5))', transition: 'all 0.3s' }} />
                    <h1 style={{ fontSize: searchQuery ? '2.5rem' : '4rem', margin: 0, fontWeight: 900, letterSpacing: '-0.02em', background: 'linear-gradient(to bottom, #fff, #999)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', transition: 'all 0.3s' }}>
                        CineMatrix
                    </h1>
                </div>

                {!searchQuery && (
                    <p style={{ color: '#a1a1aa', fontSize: '1.25rem', maxWidth: '700px', lineHeight: 1.6, marginBottom: '3rem', animation: 'fadeIn 0.5s' }}>
                        The pulse of cinema. Real-time sentiment analysis, volatility tracking, and viral insights across the global film landscape.
                    </p>
                )}

                {/* CONTENT: Featured vs Results */}
                {searchQuery ? (
                    <div style={{ width: '100%', marginTop: '2rem' }}>
                        {/* SEARCH RESULTS GRID */}
                        {filteredMovies.length > 0 ? (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '2rem', width: '100%' }}>
                                {filteredMovies.map(movie => (
                                    <MovieCard key={movie.movie_id} movie={movie} />
                                ))}
                            </div>
                        ) : (
                            <div style={{ padding: '2rem', color: '#666' }}>
                                <h3>No matches found</h3>
                            </div>
                        )}
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center', animation: 'fadeIn 0.5s' }}>
                        {jumbotronMovies.map(movie => (
                            <JumbotronCard key={movie.movie_id} movie={movie} getVolume={getVolume} />
                        ))}
                    </div>
                )}
            </div>

            {/* SECTIONS: Only visible when NOT searching */}
            {!searchQuery && (
                <>
                    {latestReleases.length > 0 && (
                        <section style={{ marginBottom: '5rem' }}>
                            <h2 style={{ fontSize: '2.25rem', marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '1rem', fontWeight: 800 }}>
                                <span style={{ width: '6px', height: '36px', background: '#646cff', borderRadius: '3px', boxShadow: '0 0 15px rgba(100, 108, 255, 0.5)' }}></span>
                                Latest Releases
                            </h2>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '2.5rem' }}>
                                {latestReleases.map(movie => (
                                    <MovieCard key={movie.movie_id} movie={movie} />
                                ))}
                            </div>
                        </section>
                    )}

                    {modernClassics.length > 0 && (
                        <section>
                            <h2 style={{ fontSize: '2.25rem', marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '1rem', fontWeight: 800 }}>
                                <span style={{ width: '6px', height: '36px', background: '#ff4757', borderRadius: '3px', boxShadow: '0 0 15px rgba(255, 71, 87, 0.5)' }}></span>
                                Modern Classics
                            </h2>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '2.5rem' }}>
                                {modernClassics.map(movie => (
                                    <MovieCard key={movie.movie_id} movie={movie} />
                                ))}
                            </div>
                        </section>
                    )}
                </>
            )}
        </div>
    );
}

// ... Card Components ...
function JumbotronCard({ movie, getVolume }: { movie: Movie, getVolume: any }) {
    return (
        <Link
            href={`/movie/${movie.movie_id}`}
            style={{ textDecoration: 'none', color: 'inherit' }}
        >
            <div
                className="card-hover-effect"
                style={{
                    cursor: 'pointer',
                    background: 'rgba(19, 19, 22, 0.6)',
                    backdropFilter: 'blur(10px)',
                    padding: '1.5rem',
                    borderRadius: '20px',
                    width: '260px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
            >
                <div style={{ width: '100%', height: '320px', background: '#1c1c1f', borderRadius: '12px', marginBottom: '1.25rem', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
                    {movie.poster_url ? (
                        <img
                            src={movie.poster_url}
                            alt={movie.title}
                            className="jumbo-poster"
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                    ) : (
                        <span style={{ fontSize: '1.5rem', fontWeight: 800, color: '#646cff', textAlign: 'center', padding: '1rem' }}>
                            {movie.title}
                        </span>
                    )}
                </div>
                <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700 }}>{movie.title}</h3>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', fontSize: '0.9rem', color: '#a1a1aa', fontWeight: 500 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <TrendingUp size={16} color="#00ff9d" />
                        {getVolume(movie.daily_sentiment_summary?.volume)} Signals
                    </span>
                </div>
            </div>
        </Link>
    );
}

function MovieCard({ movie }: { movie: Movie }) {
    return (
        <Link
            href={`/movie/${movie.movie_id}`}
            style={{ textDecoration: 'none', color: 'inherit' }}
        >
            <div
                className="card card-hover-effect"
                style={{
                    cursor: 'pointer',
                    padding: '1.25rem',
                    borderRadius: '20px',
                    background: '#131316',
                    border: '1px solid rgba(255,255,255,0.05)',
                }}
            >
                <div style={{ width: '100%', height: '280px', background: '#1c1c1f', borderRadius: '12px', marginBottom: '1.25rem', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.03)' }}>
                    {movie.poster_url ? (
                        <img
                            src={movie.poster_url}
                            alt={movie.title}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                    ) : (
                        <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#646cff', textAlign: 'center', padding: '1rem' }}>
                            {movie.title}
                        </span>
                    )}
                </div>
                <h3 style={{ fontSize: '1.2rem', margin: '0 0 0.75rem', fontWeight: 700 }}>{movie.title}</h3>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <p style={{ margin: 0, color: '#a1a1aa', fontSize: '0.9rem', fontWeight: 500 }}>
                        Sentiment
                    </p>
                    <span style={{
                        color: (movie.daily_sentiment_summary?.score || 0) > 0 ? '#00ff9d' : '#ff4757',
                        background: (movie.daily_sentiment_summary?.score || 0) > 0 ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255, 71, 87, 0.1)',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        fontWeight: 700
                    }}>
                        {movie.daily_sentiment_summary?.score ? movie.daily_sentiment_summary.score.toFixed(2) : '0.00'}
                    </span>
                </div>
            </div>
        </Link>
    );
}
