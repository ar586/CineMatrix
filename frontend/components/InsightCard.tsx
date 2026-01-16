import React from 'react';
import type { Insight } from '../services/api';
import { AlertTriangle, TrendingUp, Activity, Zap } from 'lucide-react';

interface Props {
    insight: Insight;
}

const getIcon = (type: string) => {
    switch (type) {
        case 'controversy': return <AlertTriangle color="#ff4757" />;
        case 'trend': return <TrendingUp color="#00ff9d" />;
        case 'anomaly': return <Zap color="#ffa502" />;
        default: return <Activity color="#646cff" />;
    }
};

export const InsightCard: React.FC<Props> = ({ insight }) => {
    const isHighSeverity = insight.severity === 'high';

    return (
        <div className="card" style={{
            marginTop: '1rem',
            borderColor: isHighSeverity ? '#ff4757' : undefined,
            background: isHighSeverity ? 'rgba(255, 71, 87, 0.05)' : undefined
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                {getIcon(insight.insight_type)}
                <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{insight.title}</h3>
                {isHighSeverity && <span style={{
                    background: '#ff4757', color: 'white', padding: '0.2rem 0.5rem',
                    borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold'
                }}>CRITICAL</span>}
            </div>
            <p style={{ color: '#a1a1aa', lineHeight: '1.6' }}>
                {insight.summary}
            </p>
            <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '1rem' }}>
                AI Model: {insight.generated_by?.agent || 'Unknown'} • {new Date(insight.generated_at.replace(' ', 'T')).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
            </div>
        </div>
    );
};
