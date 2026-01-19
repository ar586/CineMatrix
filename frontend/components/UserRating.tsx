'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Star } from 'lucide-react';

interface Comment {
    _id: string;
    username: string;
    text?: string;
    rating?: number;
    created_at: string;
}

export default function UserRating({ movieId }: { movieId: string }) {
    const { user, token } = useAuth();
    const [rating, setRating] = useState<number | undefined>(undefined);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (user && movieId) {
            fetchUserRating();
        }
    }, [user, movieId]);

    const fetchUserRating = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/movies/${movieId}/comments/`);
            if (res.ok) {
                const data: Comment[] = await res.json();
                // Find latest rating by this user
                const myRating = data.find(c => c.username === user?.username && c.rating);
                if (myRating) {
                    setRating(myRating.rating);
                }
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleRate = async (value: number) => {
        if (!token) return;
        setSubmitting(true);
        try {
            // Post a new comment with just rating
            const res = await fetch(`http://localhost:8000/api/movies/${movieId}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ rating: value, text: "" })
            });
            if (res.ok) {
                setRating(value);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setSubmitting(false);
        }
    };

    if (!user) {
        return (
            <div className="flex flex-col items-end min-w-[120px]">
                <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-1">Your Rating</span>
                <div className="flex gap-1" title="Log in to rate">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <a key={star} href="/login" className="cursor-pointer hover:opacity-80 transition-opacity">
                            <Star size={24} fill="none" color="#9ca3af" strokeWidth={1.5} />
                        </a>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-end min-w-[120px]">
            <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-1">Your Rating</span>
            <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        type="button"
                        disabled={submitting}
                        onClick={() => handleRate(star)}
                        className={`transition-transform hover:scale-110 focus:outline-none ${submitting ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}
                    >
                        <Star
                            size={24}
                            fill={star <= (rating || 0) ? "#fbbf24" : "none"}
                            color={star <= (rating || 0) ? "#fbbf24" : "#9ca3af"}
                            strokeWidth={1.5}
                        />
                    </button>
                ))}
            </div>
        </div>
    );
}
