import { api } from '@/services/api';
import type { Movie, DailySentiment, Insight, FeedItem, NewsArticle, RedditPost } from '@/services/api';
import { MovieDashboard } from '@/components/MovieDashboard';
import UserRating from '@/components/UserRating';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import type { Metadata, ResolvingMetadata } from 'next';

export async function generateMetadata(
    { params }: { params: Promise<{ id: string }> },
    parent: ResolvingMetadata
): Promise<Metadata> {
    const { id } = await params;

    try {
        const movie = await api.getMovie(id);
        if (!movie) return { title: 'Movie Not Found' };

        const previousImages = (await parent).openGraph?.images || [];

        return {
            title: movie.title,
            description: movie.overview || `Deep sentiment analysis and audience insights for ${movie.title}.`,
            openGraph: {
                title: `${movie.title} - Sentiment & Insights`,
                description: movie.tagline || movie.overview?.slice(0, 150) + '...',
                images: movie.poster_url ? [movie.poster_url, ...previousImages] : previousImages,
            },
            twitter: {
                card: 'summary_large_image',
                title: movie.title,
                description: movie.tagline || `Check out the AI sentiment analysis for ${movie.title}`,
                images: movie.poster_url ? [movie.poster_url] : [],
            }
        };
    } catch (error) {
        return {
            title: 'CineMatrix Movie Analysis',
            description: 'Real-time movie sentiment tracking.'
        };
    }
}

export const dynamic = 'force-dynamic';

export default async function MoviePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;

    let movie: Movie | null = null;
    let dailyData: DailySentiment[] = [];
    let insights: Insight[] = [];
    let feed: FeedItem[] = [];
    let news: NewsArticle[] = [];
    let reddit: RedditPost[] = [];

    try {
        [movie, dailyData, insights, feed, news, reddit] = await Promise.all([
            api.getMovie(id).catch(() => null), // Handle 404 gracefully
            api.getDailySentiment(id),
            api.getInsights(id),
            api.getFeed(id),
            api.getNews(id),
            api.getRedditPosts(id).catch(() => []) // Handle no Reddit data gracefully
        ]);
    } catch (error) {
        console.error('Failed to fetch movie details:', error);
    }

    const latestDay = dailyData[dailyData.length - 1];

    // Handle volume being either a number or an object
    let displayVolume = 0;
    if (latestDay?.volume) {
        if (typeof latestDay.volume === 'number') {
            displayVolume = latestDay.volume;
        } else if (typeof latestDay.volume === 'object') {
            displayVolume = (latestDay.volume.reddit_posts || 0) + (latestDay.volume.youtube_videos || 0);
        }
    }

    const currentAspects = latestDay?.aspect_summary || {};
    const criticalInsight = insights.find(i => i.severity === 'high');

    return (
        <div style={{ paddingBottom: '4rem' }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
                <button style={{ background: 'transparent', padding: '0', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#666', border: 'none', cursor: 'pointer' }}>
                    <ArrowLeft size={20} /> Back to Heatmap
                </button>
            </Link>

            {/* HEADER */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '3rem', margin: 0, fontWeight: 800 }}>{movie?.title || id}</h1>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                        {movie?.genres?.map(g => (
                            <span key={g} style={{ border: '1px solid #333', padding: '0.2rem 0.8rem', borderRadius: '15px', fontSize: '0.8rem', color: '#888' }}>
                                {g}
                            </span>
                        ))}
                        {movie?.imdb?.rating && (
                            <span style={{ color: '#f5c518', fontWeight: 'bold', fontSize: '1rem' }}>
                                ★ {movie.imdb.rating}
                            </span>
                        )}
                        <span style={{ color: '#666', fontSize: '0.9rem' }}>|</span>
                        <span style={{ background: '#1c1c21', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.9rem', color: '#a1a1aa' }}>
                            Sentiment: <span style={{ color: (latestDay?.overall_sentiment || 0) > 0 ? '#00ff9d' : '#ff4757', fontWeight: 'bold' }}>
                                {latestDay?.overall_sentiment || 0}
                            </span>
                        </span>
                        <span style={{ background: '#1c1c21', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.9rem', color: '#a1a1aa' }}>
                            Volume: {displayVolume}
                        </span>
                    </div>
                    {/* Cast & Crew Info Line */}
                    {(movie?.crew?.director || movie?.cast) && (
                        <div style={{ marginTop: '1rem', color: '#888', fontSize: '0.9rem' }}>
                            {movie?.crew?.director && <span style={{ marginRight: '1.5rem' }}>Director: <span style={{ color: '#ccc' }}>{movie.crew.director}</span></span>}
                            {movie?.cast && <span>Cast: <span style={{ color: '#ccc' }}>{movie.cast.slice(0, 3).join(", ")}</span></span>}
                        </div>
                    )}
                </div>

                {/* User Rating - Top Right */}
                <div style={{ marginTop: '0.5rem' }}>
                    <UserRating movieId={id} />
                </div>
            </div>

            {/* CRISIS ALERT - Agent-Driven Component */}
            {criticalInsight && (
                <div
                    style={{
                        background: 'rgba(255, 71, 87, 0.1)',
                        border: '1px solid #ff4757',
                        padding: '1.5rem',
                        borderRadius: '12px',
                        marginBottom: '2rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem'
                    }}
                >
                    <div style={{ fontSize: '2rem' }}>🚨</div>
                    <div>
                        <h3 style={{ margin: 0, color: '#ff4757' }}>CRITICAL ALERT: {criticalInsight.title}</h3>
                        <p style={{ margin: 0, color: '#ffbdc3' }}>{criticalInsight.summary}</p>
                    </div>
                </div>
            )}

            {/* Client Interaction Layer */}
            <MovieDashboard
                dailyData={dailyData}
                insights={insights}
                feed={feed}
                news={news}
                reddit={reddit}
                currentAspects={currentAspects}
                movie={movie}
            />
        </div>
    );
}
