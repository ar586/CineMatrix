import { api } from '@/services/api';
import type { Movie } from '@/services/api';
import Link from 'next/link';
import { Flame, TrendingUp } from 'lucide-react';
import MovieSearch from '@/components/MovieSearch';

import type { Metadata } from 'next';

export const dynamic = 'force-dynamic'; // Ensure fresh data on every request

export const metadata: Metadata = {
  title: 'Dashboard',
  description: 'Monitor real-time sentiment trends for the latest movie releases.',
};

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
