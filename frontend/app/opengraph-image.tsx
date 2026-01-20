import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = 'CineMatrix - AI Movie Sentiment';
export const size = {
    width: 1200,
    height: 630,
};
export const contentType = 'image/png';

export default async function Image() {
    return new ImageResponse(
        (
            <div
                style={{
                    background: 'linear-gradient(to bottom right, #000000, #1a1a1a)',
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'sans-serif',
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                    <div
                        style={{
                            fontSize: 80,
                            fontWeight: 'bold',
                            background: 'linear-gradient(to right, #646cff, #00ff9d)',
                            backgroundClip: 'text',
                            color: 'transparent',
                            display: 'flex',
                        }}
                    >
                        CineMatrix
                    </div>
                </div>
                <div
                    style={{
                        fontSize: 30,
                        color: '#a1a1aa',
                        textAlign: 'center',
                        maxWidth: '800px',
                        lineHeight: 1.4,
                    }}
                >
                    Real-time AI Sentiment Analysis for Movies
                </div>
                <div style={{ display: 'flex', marginTop: '40px', gap: '20px' }}>
                    <div style={{ background: '#333', padding: '10px 20px', borderRadius: '20px', color: '#fff' }}>Reddit</div>
                    <div style={{ background: '#333', padding: '10px 20px', borderRadius: '20px', color: '#fff' }}>YouTube</div>
                    <div style={{ background: '#333', padding: '10px 20px', borderRadius: '20px', color: '#fff' }}>News</div>
                </div>
            </div>
        ),
        {
            ...size,
        }
    );
}
