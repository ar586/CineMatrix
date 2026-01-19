import { api } from '@/services/api';
import type { Movie } from '@/services/api';
import Link from 'next/link';
import { Flame, TrendingUp } from 'lucide-react';
import MovieSearch from '@/components/MovieSearch';

export const dynamic = 'force-dynamic'; // Ensure fresh data on every request

export default async function Home() {
  let movies: Movie[] = [];
  try {
    movies = await api.getMovies();
  } catch (error) {
    console.error('Failed to fetch movies:', error);
  }

  return (
    <div style={{ paddingBottom: '4rem' }}>
      <MovieSearch initialMovies={movies} />
    </div>
  );
}

// Remove local MovieCard/Jumbotron logic as it moves to client component
