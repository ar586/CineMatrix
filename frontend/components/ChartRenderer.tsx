import { Fragment } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface ChartRendererProps {
    chartType: string;
    title: string;
    description?: string;
    data?: any[];
}

const COLORS = ['#646cff', '#00ff9d', '#ffa502', '#ff4757', '#a29bfe', '#fd79a8'];

export function ChartRenderer({ chartType, title, description, data: providedData }: ChartRendererProps) {
    // Sample data based on chart type (Fallback if no data provided)
    const getSampleData = () => {
        switch (chartType) {
            case 'line':
                return [
                    { date: 'Jan 8', sentiment: 0.82 },
                    { date: 'Jan 9', sentiment: 0.85 },
                    { date: 'Jan 10', sentiment: 0.95 },
                    { date: 'Jan 11', sentiment: 0.88 },
                    { date: 'Jan 12', sentiment: 0.90 },
                    { date: 'Jan 13', sentiment: 0.87 },
                    { date: 'Jan 14', sentiment: 0.89 }
                ];
            case 'bar':
                return [
                    { platform: 'Reddit', discussions: 145 },
                    { platform: 'YouTube', discussions: 63 },
                    { platform: 'Twitter', discussions: 28 }
                ];
            case 'pie':
                return [
                    { name: 'Reddit', value: 145 },
                    { name: 'YouTube', value: 63 },
                    { name: 'Twitter', value: 28 }
                ];
            case 'radar':
                return [
                    { aspect: 'Horror', score: 0.95 },
                    { aspect: 'Acting', score: 0.88 },
                    { aspect: 'Atmosphere', score: 0.92 },
                    { aspect: 'Story', score: 0.85 },
                    { aspect: 'Scares', score: 0.93 }
                ];
            default:
                return [];
        }
    };

    const data = (providedData && providedData.length > 0) ? providedData : getSampleData();

    const renderChart = () => {
        switch (chartType) {
            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="date" stroke="#999" />
                            <YAxis stroke="#999" domain={[0, 1]} />
                            <Tooltip
                                contentStyle={{ background: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Line type="monotone" dataKey="sentiment" stroke="#646cff" strokeWidth={3} dot={{ fill: '#646cff', r: 5 }} />
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="platform" stroke="#999" />
                            <YAxis stroke="#999" />
                            <Tooltip
                                contentStyle={{ background: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Bar dataKey="discussions" fill="#646cff" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ background: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                );

            case 'radar':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <RadarChart data={data}>
                            <PolarGrid stroke="#333" />
                            <PolarAngleAxis dataKey="aspect" stroke="#999" />
                            <PolarRadiusAxis stroke="#999" domain={[0, 1]} />
                            <Radar name="Score" dataKey="score" stroke="#646cff" fill="#646cff" fillOpacity={0.6} />
                            <Tooltip
                                contentStyle={{ background: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                );

            case 'heatmap': {
                // Custom heatmap implementation
                const heatmapData = [
                    { day: 'Mon', hour: '00:00', value: 12 },
                    { day: 'Mon', hour: '06:00', value: 45 },
                    { day: 'Mon', hour: '12:00', value: 89 },
                    { day: 'Mon', hour: '18:00', value: 156 },
                    { day: 'Tue', hour: '00:00', value: 8 },
                    { day: 'Tue', hour: '06:00', value: 34 },
                    { day: 'Tue', hour: '12:00', value: 92 },
                    { day: 'Tue', hour: '18:00', value: 142 },
                    { day: 'Wed', hour: '00:00', value: 15 },
                    { day: 'Wed', hour: '06:00', value: 52 },
                    { day: 'Wed', hour: '12:00', value: 98 },
                    { day: 'Wed', hour: '18:00', value: 178 }
                ];
                const maxValue = Math.max(...heatmapData.map(d => d.value));
                const days = ['Mon', 'Tue', 'Wed'];
                const hours = ['00:00', '06:00', '12:00', '18:00'];

                return (
                    <div style={{ padding: '1rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '60px repeat(4, 1fr)', gap: '4px' }}>
                            <div></div>
                            {hours.map(hour => (
                                <div key={hour} style={{ textAlign: 'center', fontSize: '0.75rem', color: '#999' }}>
                                    {hour}
                                </div>
                            ))}
                            {days.map(day => (
                                <Fragment key={day}>
                                    <div key={`label-${day}`} style={{ display: 'flex', alignItems: 'center', fontSize: '0.75rem', color: '#999' }}>
                                        {day}
                                    </div>
                                    {hours.map(hour => {
                                        const cell = heatmapData.find(d => d.day === day && d.hour === hour);
                                        const intensity = cell ? cell.value / maxValue : 0;
                                        return (
                                            <div
                                                key={`${day}-${hour}`}
                                                style={{
                                                    background: `rgba(100, 108, 255, ${intensity})`,
                                                    borderRadius: '4px',
                                                    aspectRatio: '1',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '0.7rem',
                                                    color: intensity > 0.5 ? '#fff' : '#999',
                                                    cursor: 'pointer',
                                                    transition: 'transform 0.2s',
                                                    border: '1px solid #333'
                                                }}
                                                title={`${day} ${hour}: ${cell?.value || 0} discussions`}
                                                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                            >
                                                {cell?.value || 0}
                                            </div>
                                        );
                                    })}
                                </Fragment>
                            ))}
                        </div>
                        <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: '#999' }}>
                            <span>Low</span>
                            <div style={{ flex: 1, height: '8px', background: 'linear-gradient(to right, rgba(100, 108, 255, 0.1), rgba(100, 108, 255, 1))', borderRadius: '4px' }} />
                            <span>High</span>
                        </div>
                    </div>
                );
            }

            case 'gauge': {
                // Custom gauge/meter implementation
                const gaugeValue = 0.87; // 87%
                const gaugeAngle = (gaugeValue * 180) - 90; // -90 to 90 degrees

                return (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '2rem',
                        minHeight: '250px'
                    }}>
                        <div style={{ position: 'relative', width: '200px', height: '120px' }}>
                            {/* Background arc */}
                            <svg width="200" height="120" style={{ position: 'absolute' }}>
                                <path
                                    d="M 20 100 A 80 80 0 0 1 180 100"
                                    fill="none"
                                    stroke="#333"
                                    strokeWidth="20"
                                    strokeLinecap="round"
                                />
                                {/* Colored arc */}
                                <path
                                    d="M 20 100 A 80 80 0 0 1 180 100"
                                    fill="none"
                                    stroke="url(#gaugeGradient)"
                                    strokeWidth="20"
                                    strokeLinecap="round"
                                    strokeDasharray={`${gaugeValue * 251} 251`}
                                />
                                <defs>
                                    <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#ff4757" />
                                        <stop offset="50%" stopColor="#ffa502" />
                                        <stop offset="100%" stopColor="#00ff9d" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            {/* Needle */}
                            <div style={{
                                position: 'absolute',
                                bottom: '20px',
                                left: '50%',
                                width: '4px',
                                height: '70px',
                                background: '#fff',
                                transformOrigin: 'bottom center',
                                transform: `translateX(-50%) rotate(${gaugeAngle}deg)`,
                                borderRadius: '2px',
                                boxShadow: '0 0 10px rgba(255,255,255,0.5)',
                                transition: 'transform 0.5s ease-out'
                            }} />
                            {/* Center dot */}
                            <div style={{
                                position: 'absolute',
                                bottom: '15px',
                                left: '50%',
                                width: '12px',
                                height: '12px',
                                background: '#fff',
                                borderRadius: '50%',
                                transform: 'translateX(-50%)',
                                boxShadow: '0 0 10px rgba(255,255,255,0.5)'
                            }} />
                        </div>
                        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00ff9d' }}>
                                {(gaugeValue * 100).toFixed(0)}%
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#999', marginTop: '0.25rem' }}>
                                Overall Sentiment Score
                            </div>
                        </div>
                    </div>
                );
            }

            case 'indicator': {
                // Single metric indicator with trend
                const indicatorValue = 0.88;
                const previousValue = 0.82;
                const change = indicatorValue - previousValue;
                const changePercent = ((change / previousValue) * 100).toFixed(1);
                const isPositive = change > 0;

                return (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '2rem',
                        minHeight: '250px'
                    }}>
                        <div style={{
                            fontSize: '4rem',
                            fontWeight: 'bold',
                            background: 'linear-gradient(135deg, #646cff 0%, #00ff9d 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            backgroundClip: 'text',
                            marginBottom: '0.5rem'
                        }}>
                            {(indicatorValue * 100).toFixed(0)}%
                        </div>

                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            marginBottom: '1rem'
                        }}>
                            <span style={{
                                color: isPositive ? '#00ff9d' : '#ff4757',
                                fontSize: '1.2rem',
                                fontWeight: 'bold'
                            }}>
                                {isPositive ? '↑' : '↓'} {Math.abs(parseFloat(changePercent))}%
                            </span>
                            <span style={{ color: '#999', fontSize: '0.9rem' }}>
                                vs. previous period
                            </span>
                        </div>

                        <div style={{
                            display: 'flex',
                            gap: '2rem',
                            marginTop: '1rem',
                            padding: '1rem',
                            background: '#18181b',
                            borderRadius: '8px',
                            width: '100%',
                            justifyContent: 'space-around'
                        }}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>
                                    CURRENT
                                </div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#00ff9d' }}>
                                    {(indicatorValue * 100).toFixed(0)}%
                                </div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>
                                    PREVIOUS
                                </div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#999' }}>
                                    {(previousValue * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                    </div>
                );
            }

            default:
                return (
                    <div style={{
                        height: '250px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#666'
                    }}>
                        <p>Chart type "{chartType}" not yet supported</p>
                    </div>
                );
        }
    };

    return (
        <div style={{
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
            borderRadius: '8px',
            padding: '1.5rem',
            border: '1px solid #333'
        }}>
            {renderChart()}
        </div>
    );
}
