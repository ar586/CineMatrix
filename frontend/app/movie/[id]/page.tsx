import { api } from '@/services/api';
import type { DailySentiment, Insight, FeedItem } from '@/services/api';
import { MovieDashboard } from '@/components/MovieDashboard';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default async function MoviePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;

    let dailyData: DailySentiment[] = [];
    let insights: Insight[] = [];
    let feed: FeedItem[] = [];

    try {
        [dailyData, insights, feed] = await Promise.all([
            api.getDailySentiment(id),
            api.getInsights(id),
            api.getFeed(id)
        ]);
    } catch (error) {
        console.error('Failed to fetch movie details:', error);
    }

    const latestDay = dailyData[dailyData.length - 1];
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '3rem', margin: 0, fontWeight: 800 }}>{id}</h1>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                        <span style={{ background: '#1c1c21', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.9rem', color: '#a1a1aa' }}>
                            Sentiment: <span style={{ color: (latestDay?.overall_sentiment || 0) > 0 ? '#00ff9d' : '#ff4757', fontWeight: 'bold' }}>
                                {latestDay?.overall_sentiment || 0}
                            </span>
                        </span>
                        <span style={{ background: '#1c1c21', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.9rem', color: '#a1a1aa' }}>
                            Volume: {latestDay?.volume || 0}
                        </span>
                    </div>
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
                currentAspects={currentAspects}
            />
        </div>
    );
}
