'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { DailySentiment } from '../services/api';

interface Props {
    data: DailySentiment[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { value: number }[]; label?: string }) => {
    if (active && payload && payload.length) {
        return (
            <div className="card" style={{ padding: '0.5rem', background: '#131316', border: '1px solid #27272a' }}>
                <p style={{ margin: 0, color: '#a1a1aa' }}>{new Date(label || '').toLocaleDateString()}</p>
                <p style={{ margin: 0, fontWeight: 'bold' }}>
                    Score: <span style={{ color: '#00ff9d' }}>{payload[0].value}</span>
                </p>
            </div>
        );
    }
    return null;
};

export const SentimentChart: React.FC<Props> = ({ data }) => {
    // Transform data for chart if needed, or use as is
    return (
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis
                        dataKey="date"
                        stroke="#a1a1aa"
                        tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    />
                    <YAxis stroke="#a1a1aa" domain={[-1, 1]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line
                        type="monotone"
                        dataKey="overall_sentiment"
                        stroke="#646cff"
                        strokeWidth={3}
                        dot={{ fill: '#646cff' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};
