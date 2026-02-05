import React from 'react';
import EmotionIndicator from '../EmotionIndicator/EmotionIndicator';
import type { Message } from '../../types/api';
import './MessageBubble.css';

interface MessageBubbleProps {
    message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isUser = message.role === 'user';
    const animationClass = isUser ? 'animate-slide-in-right' : 'animate-slide-in-left';

    const formatTime = (date: Date) => {
        return new Intl.DateTimeFormat('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        }).format(date);
    };

    return (
        <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--assistant'} ${animationClass}`}>
            <div className="message-bubble__content">
                {!isUser && message.emotion && (
                    <div className="message-bubble__emotion">
                        <EmotionIndicator emotion={message.emotion} size="small" />
                    </div>
                )}

                <div className="message-bubble__text">
                    {message.content}
                </div>

                {!isUser && message.action && (
                    <div className="message-bubble__action-badge">
                        {message.action.replace(/_/g, ' ')}
                    </div>
                )}
            </div>

            <div className="message-bubble__timestamp">
                {formatTime(message.timestamp)}
            </div>
        </div>
    );
};

export default MessageBubble;
