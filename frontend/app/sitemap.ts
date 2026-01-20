import { MetadataRoute } from 'next';
import { api } from '@/services/api';

export const dynamic = 'force-dynamic';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:4000';

    // Static routes
    const routes = [
        '',
        '/login',
        '/register',
    ].map((route) => ({
        url: `${baseUrl}${route}`,
        lastModified: new Date(),
        changeFrequency: 'daily' as const,
        priority: route === '' ? 1 : 0.8,
    }));

    try {
        const movies = await api.getMovies();

        const movieRoutes = movies.map((movie) => ({
            url: `${baseUrl}/movie/${movie.movie_id || movie._id}`,
            lastModified: new Date(),
            changeFrequency: 'daily' as const,
            priority: 0.7,
        }));

        return [...routes, ...movieRoutes];
    } catch (error) {
        console.error('Failed to generate movie sitemap:', error);
        return routes;
    }
}
