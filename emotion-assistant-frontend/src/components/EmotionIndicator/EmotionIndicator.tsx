import React from 'react';
import './EmotionIndicator.css';

interface EmotionIndicatorProps {
    emotion?: string;
    size?: 'small' | 'medium' | 'large';
}

const EmotionIndicator: React.FC<EmotionIndicatorProps> = ({
    emotion = 'neutral',
    size = 'medium'
}) => {
    const sizeClass = `emotion-indicator--${size}`;
    const emotionClass = `emotion-indicator--${emotion.toLowerCase()}`;

    return (
        <div
            className={`emotion-indicator ${sizeClass} ${emotionClass}`}
            title={emotion}
            aria-label={`Current emotion: ${emotion}`}
        >
            <div className="emotion-indicator__glow"></div>
            <div className="emotion-indicator__core"></div>
        </div>
    );
};

export default EmotionIndicator;
