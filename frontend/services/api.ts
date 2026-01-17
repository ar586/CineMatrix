import axios from 'axios';

const isServer = typeof window === 'undefined';
const API_BASE = isServer
    ? (process.env.INTERNAL_API_URL || 'http://localhost:8000/api')
    : '/api';

export interface Movie {
    _id: string;
    wikipedia?: {
        page_title?: string;
        summary?: string;
        url?: string;
        sections?: Array<{
            title: string;
            content: string;
            level: number;
        }>;
    };
    movie_id: string;
    title: string;
    production_companies?: string[];
    trailers?: Array<{
        key: string;
        name: string;
        type: string;
    }>;
    collection?: {
        id: number;
        name: string;
        poster?: string;
    };
    backdrop_url?: string;
    poster_url?: string;
    tagline?: string;
    overview?: string;
    genres?: string[];
    cast?: string[];
    crew?: {
        director?: string;
        writers?: string[];
    };
    imdb?: {
        rating?: number;
        votes?: number;
    };
    rotten_tomatoes?: {
        critics_score?: number;
    };
    metascore?: number;
    vote_average?: number;
    release_date?: string;
    runtime_minutes?: number;
    budget?: number;
    revenue?: number;
    certification?: {
        US?: string;
    };
    box_office?: string;
    awards?: string;
    // IMDB flat fields (for backward compatibility)
    year?: string;
    rated?: string;
    runtime?: string;
    genre?: string | string[];
    director?: string;
    actors?: string | string[];
    plot?: string;
    poster?: string;
    imdb_rating?: number;
    imdb_votes?: number;
    daily_sentiment_summary: {
        score: number;
        volume: number | { reddit_posts: number; youtube_videos: number };
        volatility: number;
    } | null;
}

export interface DailySentiment {
    date: string;
    overall_sentiment: number;
    volume: number | { reddit_posts: number; youtube_videos: number };
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

export interface RedditComment {
    comment_id: string;
    text: string;
    score: number;
    created_at: string;
}

export interface RedditPost {
    _id: string;
    post_id: string;
    subreddit: string;
    title: string;
    selftext?: string;
    url: string;
    score: number;
    num_comments: number;
    created_at: string;
    comments: RedditComment[];
    sentiment?: {
        score: number;
        label: string;
        confidence: number;
    };
}

export interface YouTubeComment {
    comment_id: string;
    text: string;
    likes: number;
    created_at: string;
}

export interface YouTubeVideo {
    id?: string;
    video_id: string;
    video_type: string;
    title: string;
    channel: string;
    channel_id?: string;
    channel_image?: string;
    channel_subs?: string;
    url: string;
    transcript?: string;
    published_at: string;
    stats?: {
        views: number;
        likes: number;
        comment_count: number;
    };
    comments: YouTubeComment[];
    sentiment?: {
        score: number;
        label: string;
        confidence: number;
    };
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
    },
    getRedditPosts: async (movieId: string) => {
        const response = await axios.get<RedditPost[]>(`${API_BASE}/movies/${movieId}/reddit`);
        return response.data;
    },
    getMovieYoutubeVideos: async (movieId: string) => {
        const response = await axios.get<YouTubeVideo[]>(`${API_BASE}/movies/${movieId}/youtube`);
        return response.data;
    }
};
