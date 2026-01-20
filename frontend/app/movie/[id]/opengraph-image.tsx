import { ImageResponse } from 'next/og';
import { api } from '@/services/api';

export const runtime = 'edge';
export const alt = 'Movie Sentiment Analysis';
export const size = {
    width: 1200,
    height: 630,
};
export const contentType = 'image/png';

export default async function Image({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;

    // Default values
    let title = 'Movie Analysis';
    let sentimentScore = 0;
    let year = '';

    try {
        // Note: In edge runtime we might need to use fetch directly if api service isn't edge compatible
        // But assuming api service uses standard fetch:
        const baseUrl = process.env.INTERNAL_API_URL || 'http://localhost:7000/api';
        const res = await fetch(`${baseUrl}/movies/${id}`);
        if (res.ok) {
            const movie = await res.json();
            title = movie.title;
            year = movie.release_date ? movie.release_date.split('-')[0] : '';
            sentimentScore = movie.daily_sentiment_summary?.score || 0;
        }
    } catch (e) {
        console.error("OG Image Fetch Error", e);
    }

    const isPositive = sentimentScore > 0;
    const sentimentColor = isPositive ? '#00ff9d' : '#ff4757';

    return new ImageResponse(
        (
            <div
                style={{
                    background: '#09090b',
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    padding: '60px',
                    fontFamily: 'sans-serif',
                    border: '20px solid #1f1f22'
                }}
            >
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{
                        fontSize: 32,
                        background: 'linear-gradient(to right, #646cff, #a29bfe)',
                        backgroundClip: 'text',
                        color: 'transparent',
                        fontWeight: 'bold',
                        marginBottom: '20px'
                    }}>
                        CineMatrix AI Analysis
                    </div>
                    <div style={{ fontSize: 70, fontWeight: 'bold', color: 'white', lineHeight: 1.1 }}>
                        {title}
                    </div>
                    {year && (
                        <div style={{ fontSize: 40, color: '#a1a1aa', marginTop: '10px' }}>
                            ({year})
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <div style={{ fontSize: 24, color: '#a1a1aa', marginBottom: '10px' }}>AI Sentiment Score</div>
                        <div style={{
                            fontSize: 120,
                            fontWeight: 'bold',
                            color: sentimentColor,
                            lineHeight: 1
                        }}>
                            {sentimentScore > 0 ? '+' : ''}{sentimentScore.toFixed(2)}
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ fontSize: 24, color: '#555' }}>Reddit</div>
                        <div style={{ fontSize: 24, color: '#555' }}>•</div>
                        <div style={{ fontSize: 24, color: '#555' }}>YouTube</div>
                        <div style={{ fontSize: 24, color: '#555' }}>•</div>
                        <div style={{ fontSize: 24, color: '#555' }}>News</div>
                    </div>
                </div>
            </div>
        ),
        {
            ...size,
        }
    );
}
