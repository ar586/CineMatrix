import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface Movie {
    _id: string;
    movie_id: string;
    title: string;
    genres?: string[];
    cast?: string[];
    crew?: {
        director?: string;
        writers?: string[];
    };
    imdb?: {
        rating?: number;
    };
    rotten_tomatoes?: {
        critics_score?: number;
    };
    metascore?: number;
    box_office?: string;
    awards?: string;
    daily_sentiment_summary: {
        score: number;
        volume: number;
        volatility: number;
    } | null;
}

export interface DailySentiment {
    date: string;
    overall_sentiment: number;
    volume: number;
    volatility: number;
    aspect_summary?: Record<string, number>;
}

export interface Insight {
    _id: string;
    title: string;
    summary: string;
    insight_type: string;
    severity: string;
    recommended_visual: {
        component: string;
        x: string;
        y: string[];
    };
    generated_at: string;
    generated_by?: {
        agent: string;
    };
}

export interface FeedItem {
    _id: string;
    source: string;
    text: string;
    url: string;
    sentiment: {
        score: number;
        label: string;
    };
    created_at: string;
}

export interface NewsArticle {
    _id: string;
    title: string;
    url: string;
    source: string;
    published_date: string;
    insights: string[];
    category: string;
    sentiment: string;
    relevance_score: number;
}

export const api = {
    getMovies: async () => {
        const response = await axios.get<Movie[]>(`${API_BASE}/movies`);
        return response.data;
    },
    getDailySentiment: async (movieId: string) => {
        const response = await axios.get<DailySentiment[]>(`${API_BASE}/movies/${movieId}/daily`);
        return response.data;
    },
    getMovie: async (movieId: string) => {
        const response = await axios.get<Movie>(`${API_BASE}/movies/${movieId}`);
        return response.data;
    },
    getInsights: async (movieId: string) => {
        const response = await axios.get<Insight[]>(`${API_BASE}/movies/${movieId}/insights`);
        return response.data;
    },
    getFeed: async (movieId: string) => {
        const response = await axios.get<FeedItem[]>(`${API_BASE}/movies/${movieId}/feed`);
        return response.data;
    },
    getNews: async (movieId: string) => {
        const response = await axios.get<NewsArticle[]>(`${API_BASE}/movies/${movieId}/news`);
        return response.data;
    }
};
