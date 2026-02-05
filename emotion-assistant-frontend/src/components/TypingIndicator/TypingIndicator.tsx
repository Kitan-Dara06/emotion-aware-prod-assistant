import React from 'react';
import './TypingIndicator.css';

const TypingIndicator: React.FC = () => {
    return (
        <div className="typing-indicator animate-slide-in-left">
            <div className="typing-indicator__content">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
            </div>
        </div>
    );
};

export default TypingIndicator;
