import { api } from '@/services/api';
import type { Movie } from '@/services/api';
import Link from 'next/link';
import { Flame, TrendingUp } from 'lucide-react';

export const dynamic = 'force-dynamic'; // Ensure fresh data on every request

export default async function Home() {
  let movies: Movie[] = [];
  try {
    movies = await api.getMovies();
  } catch (error) {
    console.error('Failed to fetch movies:', error);
  }

  // Sort by "Heat" (Volatility + Volume)
  const hotMovies = [...movies].sort((a, b) => {
    const scoreA = (a.daily_sentiment_summary?.volatility || 0) * 10 + (a.daily_sentiment_summary?.volume || 0);
    const scoreB = (b.daily_sentiment_summary?.volatility || 0) * 10 + (b.daily_sentiment_summary?.volume || 0);
    return scoreB - scoreA;
  }).slice(0, 3);

  return (
    <div style={{ paddingBottom: '4rem' }}>
      {/* JUMBOTRON */}
      <div
        style={{
          marginBottom: '4rem',
          padding: '3rem',
          background: 'linear-gradient(135deg, #0a0a0c 0%, #1c1c21 100%)',
          borderRadius: '24px',
          border: '1px solid #27272a',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Flame size={48} color="#ff4757" />
          <h1 style={{ fontSize: '3rem', margin: 0, fontWeight: 800 }}>Box Office Heat</h1>
        </div>
        <p style={{ color: '#a1a1aa', fontSize: '1.2rem', maxWidth: '600px' }}>
          Tracking real-time sentiment volatility and viral spikes across the cinematic universe.
        </p>

        <div style={{ display: 'flex', gap: '2rem', marginTop: '3rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {hotMovies.map(movie => (
            <Link
              key={movie.movie_id}
              href={`/movie/${movie.movie_id}`}
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <div
                className="card-hover-effect"
                style={{
                  cursor: 'pointer',
                  background: '#131316',
                  padding: '1.5rem',
                  borderRadius: '16px',
                  width: '250px',
                  border: '1px solid #27272a',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                  transition: 'transform 0.2s'
                }}
              >
                <div style={{ width: '100%', height: '300px', background: 'linear-gradient(135deg, #1c1c21 0%, #27272a 100%)', borderRadius: '8px', marginBottom: '1rem', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#646cff', textAlign: 'center', padding: '1rem' }}>
                    {movie.title}
                  </span>
                </div>
                <h3 style={{ margin: '0 0 0.5rem' }}>{movie.title}</h3>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', fontSize: '0.9rem', color: '#a1a1aa' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <TrendingUp size={14} color="#00ff9d" />
                    {movie.daily_sentiment_summary?.volume || 0} Vol
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ACTIVE GRID */}
      <h2 style={{ fontSize: '2rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span style={{ width: '8px', height: '32px', background: '#646cff', borderRadius: '4px' }}></span>
        Active Releases
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '2rem' }}>
        {movies.map(movie => (
          <Link
            key={movie.movie_id}
            href={`/movie/${movie.movie_id}`}
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <div
              className="card"
              style={{ cursor: 'pointer', padding: '1rem', transition: 'transform 0.2s' }}
            >
              <div style={{ width: '100%', height: '250px', background: 'linear-gradient(135deg, #1c1c21 0%, #27272a 100%)', borderRadius: '8px', marginBottom: '1rem', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#646cff', textAlign: 'center', padding: '1rem' }}>
                  {movie.title}
                </span>
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: '0 0 0.5rem' }}>{movie.title}</h3>
              <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                Sentiment: <span style={{ color: (movie.daily_sentiment_summary?.score || 0) > 0 ? '#00ff9d' : '#ff4757' }}>
                  {movie.daily_sentiment_summary?.score || 0}
                </span>
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
