import React, { useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import Header from '../Header/Header';
import MessageBubble from '../MessageBubble/MessageBubble';
import ChatInput from '../ChatInput/ChatInput';
import TypingIndicator from '../TypingIndicator/TypingIndicator';
import './ChatContainer.css';

interface ChatContainerProps {
    userId: string;
    userEmail?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ userId, userEmail }) => {
    const { messages, isLoading, error, currentEmotion, sendMessage, clearHistory, clearError } = useChat();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSendMessage = async (content: string) => {
        await sendMessage(content, userId, userEmail);
    };

    const handleClearHistory = async () => {
        if (window.confirm('Are you sure you want to clear all conversation history?')) {
            await clearHistory(userId);
        }
    };

    return (
        <div className="chat-container">
            <Header
                currentEmotion={currentEmotion || undefined}
                onClearHistory={messages.length > 0 ? handleClearHistory : undefined}
            />

            <div className="chat-container__messages">
                {messages.length === 0 && !isLoading && (
                    <div className="chat-container__empty-state">
                        <div className="chat-container__empty-icon">💬</div>
                        <h2 className="chat-container__empty-title">
                            Welcome to Your Emotion-Aware Assistant
                        </h2>
                        <p className="chat-container__empty-description">
                            I'm here to help you with productivity tasks while understanding how you feel.
                            Share what's on your mind, and I'll provide empathetic support.
                        </p>
                        <div className="chat-container__suggestions">
                            <button
                                className="chat-container__suggestion"
                                onClick={() => handleSendMessage("I'm feeling overwhelmed with my tasks")}
                            >
                                "I'm feeling overwhelmed..."
                            </button>
                            <button
                                className="chat-container__suggestion"
                                onClick={() => handleSendMessage("Can you help me schedule a meeting?")}
                            >
                                "Help me schedule..."
                            </button>
                            <button
                                className="chat-container__suggestion"
                                onClick={() => handleSendMessage("I need to prioritize my work")}
                            >
                                "Prioritize my work"
                            </button>
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))}

                {isLoading && <TypingIndicator />}

                {error && (
                    <div className="chat-container__error">
                        <div className="chat-container__error-content">
                            <span className="chat-container__error-icon">⚠️</span>
                            <span className="chat-container__error-text">{error}</span>
                            <button
                                className="chat-container__error-dismiss"
                                onClick={clearError}
                                aria-label="Dismiss error"
                            >
                                ×
                            </button>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
    );
};

export default ChatContainer;
