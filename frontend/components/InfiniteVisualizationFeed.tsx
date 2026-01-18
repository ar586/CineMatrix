import { useEffect, useState, useRef } from 'react';
import { api, type NewsArticle } from '@/services/api';
import { ChartRenderer } from './ChartRenderer';

interface Visualization {
    id: string;
    type: 'statistic' | 'chart' | 'text_card' | 'custom';
    priority: number;
    component: {
        chart_type?: string;
        card_type?: string;
        content?: string;
        source?: string;
        title: string;
        description: string;
        data_query?: string;
        styling?: {
            color_scheme?: string;
            theme?: string;
        };
    };
}

interface VisualizationResponse {
    page: number;
    total_pages: number;
    has_more: boolean;
    visualizations: Visualization[];
    generated_at?: string;
}

interface Props {
    movieId: string;
}

export function InfiniteVisualizationFeed({ movieId }: Props) {
    const [visualizations, setVisualizations] = useState<Visualization[]>([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const observerRef = useRef<HTMLDivElement>(null);

    // Fetch visualizations
    const fetchVisualizations = async (pageNum: number) => {
        if (loading || !hasMore) return;

        setLoading(true);
        try {
            const response = await fetch(`/api/movies/${movieId}/visualizations?page=${pageNum}&limit=5`);
            const data: VisualizationResponse = await response.json();

            setVisualizations(prev => [...prev, ...data.visualizations]);
            setHasMore(data.has_more);
            setPage(pageNum + 1);
        } catch (error) {
            console.error('Failed to fetch visualizations:', error);
        } finally {
            setLoading(false);
        }
    };

    // Intersection Observer for infinite scroll
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hasMore && !loading) {
                    fetchVisualizations(page);
                }
            },
            { threshold: 0.8 }
        );

        if (observerRef.current) {
            observer.observe(observerRef.current);
        }

        return () => observer.disconnect();
    }, [page, hasMore, loading]);

    // Initial load
    useEffect(() => {
        fetchVisualizations(1);
    }, [movieId]);

    return (
        <div style={{
            background: '#121212', // Slightly darker than card for the "page" background
            borderRadius: '16px',
            border: '1px solid #333',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {visualizations.map((viz, index) => (
                <VisualizationCard key={`${viz.id}-${index}`} visualization={viz} />
            ))}

            {loading && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {[1, 2].map(i => (
                        <SkeletonLoader key={i} />
                    ))}
                </div>
            )}

            {/* Intersection observer target */}
            <div ref={observerRef} style={{ height: '20px' }} />

            {!hasMore && visualizations.length > 0 && (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                    <p>🎉 You've reached the end of insights!</p>
                </div>
            )}
        </div>
    );
}

function VisualizationCard({ visualization }: { visualization: Visualization }) {
    const { component, type } = visualization;

    const renderContent = () => {
        if (type === 'text_card' || component.card_type) {
            const themeColors: Record<string, string> = {
                'alert': '#ff4757',
                'info': '#646cff',
                'highlight': '#00ff9d',
                'default': '#a1a1aa'
            };
            const theme = component.styling?.theme || 'default';
            const color = themeColors[theme] || themeColors['default'];

            return (
                <div style={{
                    background: 'linear-gradient(135deg, rgba(100, 108, 255, 0.1) 0%, rgba(100, 108, 255, 0.05) 100%)',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    borderLeft: `4px solid ${color}`,
                    marginTop: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center'
                }}>
                    <h4 style={{ margin: '0 0 0.5rem', fontSize: '1.2rem', color: '#fff' }}>
                        {component.title}
                    </h4>
                    <p style={{ fontSize: '1rem', lineHeight: '1.6', color: '#ddd', marginBottom: '0.5rem' }}>
                        {component.content || component.description}
                    </p>
                    {component.source && (
                        <div style={{ fontSize: '0.8rem', color: '#666', fontStyle: 'italic' }}>
                            Source: {component.source}
                        </div>
                    )}
                </div>
            );
        }

        // Default to Chart
        return (
            <ChartRenderer
                chartType={component.chart_type || 'line'}
                title={component.title}
                description={component.description}
            />
        );
    };

    return (
        <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid #2a2a2a',
            background: type === 'text_card' ? '#161618' : 'transparent',
            transition: 'background 0.3s ease'
        }}>
            <div style={{ display: 'flex', alignItems: 'start', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1 }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                        {type === 'text_card' ? '📝' : getChartIcon(component.chart_type)} {component.title}
                    </h3>
                    {type !== 'text_card' && (
                        <p style={{ margin: 0, color: '#999', fontSize: '0.9rem' }}>
                            {component.description}
                        </p>
                    )}
                </div>
                <span style={{
                    background: getColorScheme(component.styling?.color_scheme),
                    color: '#000',
                    padding: '0.3rem 0.6rem',
                    borderRadius: '8px',
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    textTransform: 'uppercase'
                }}>
                    {component.chart_type || component.card_type || type}
                </span>
            </div>

            {renderContent()}


        </div>
    );
}

function SkeletonLoader() {
    return (
        <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1 }}>
                    <div style={{
                        height: '24px',
                        width: '60%',
                        background: 'linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%)',
                        backgroundSize: '200% 100%',
                        animation: 'shimmer 1.5s infinite',
                        borderRadius: '4px',
                        marginBottom: '0.5rem'
                    }} />
                    <div style={{
                        height: '16px',
                        width: '80%',
                        background: 'linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%)',
                        backgroundSize: '200% 100%',
                        animation: 'shimmer 1.5s infinite',
                        borderRadius: '4px'
                    }} />
                </div>
            </div>
            <div style={{
                height: '200px',
                background: 'linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%)',
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s infinite',
                borderRadius: '8px'
            }} />
        </div>
    );
}

function getChartIcon(chartType?: string): string {
    const icons: Record<string, string> = {
        line: '📈',
        bar: '📊',
        pie: '🥧',
        radar: '🎯',
        heatmap: '🔥',
        scatter: '⚡'
    };
    return icons[chartType || ''] || '📊';
}

function getColorScheme(scheme?: string): string {
    const schemes: Record<string, string> = {
        'sentiment-based': '#00ff9d',
        'vibrant': '#646cff',
        'monochrome': '#a1a1aa'
    };
    return schemes[scheme || ''] || '#646cff';
}
