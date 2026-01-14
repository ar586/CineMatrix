'use client';

import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface Props {
    aspects: Record<string, number>; // e.g. {"acting": 0.8, "plot": -0.2}
}

export const AspectRadar: React.FC<Props> = ({ aspects }) => {
    if (!aspects) return null;

    const data = Object.keys(aspects).map(key => ({
        subject: key.charAt(0).toUpperCase() + key.slice(1),
        A: aspects[key],
        fullMark: 1,
    }));

    return (
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                    <PolarGrid stroke="#27272a" />
                    <PolarAngleAxis dataKey="subject" stroke="#ffffff" />
                    <PolarRadiusAxis angle={30} domain={[-1, 1]} stroke="#a1a1aa" />
                    <Radar
                        name="Sentiment"
                        dataKey="A"
                        stroke="#00ff9d"
                        fill="#00ff9d"
                        fillOpacity={0.4}
                    />
                    <Tooltip />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};
