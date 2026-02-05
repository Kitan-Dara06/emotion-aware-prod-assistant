import React from 'react';
import EmotionIndicator from '../EmotionIndicator/EmotionIndicator';
import './Header.css';

interface HeaderProps {
    currentEmotion?: string;
    onClearHistory?: () => void;
}

const Header: React.FC<HeaderProps> = ({ currentEmotion, onClearHistory }) => {
    return (
        <header className="header glass">
            <div className="header__content">
                <div className="header__branding">
                    <h1 className="header__title">
                        <span className="header__emoji">🧠</span>
                        Emotion-Aware Assistant
                    </h1>
                </div>

                <div className="header__status">
                    {currentEmotion && (
                        <div className="header__emotion">
                            <EmotionIndicator emotion={currentEmotion} size="small" />
                            <span className="header__emotion-label">{currentEmotion}</span>
                        </div>
                    )}

                    {onClearHistory && (
                        <button
                            className="header__clear-btn"
                            onClick={onClearHistory}
                            title="Clear conversation history"
                        >
                            <svg
                                width="18"
                                height="18"
                                viewBox="0 0 24 24"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>
                        </button>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
