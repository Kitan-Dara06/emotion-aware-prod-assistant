import React, { useState, useRef, useEffect } from 'react';
import './ChatInput.css';

interface ChatInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled = false }) => {
    const [message, setMessage] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSend(message.trim());
            setMessage('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);

        // Auto-expand textarea
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    };

    useEffect(() => {
        if (!disabled && textareaRef.current) {
            textareaRef.current.focus();
        }
    }, [disabled]);

    return (
        <form className="chat-input" onSubmit={handleSubmit}>
            <div className="chat-input__container glass">
                <textarea
                    ref={textareaRef}
                    className="chat-input__textarea"
                    placeholder="Share how you're feeling or what you need help with..."
                    value={message}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    rows={1}
                    maxLength={2000}
                />

                <button
                    type="submit"
                    className={`chat-input__button ${disabled ? 'chat-input__button--disabled' : ''}`}
                    disabled={disabled || !message.trim()}
                    aria-label="Send message"
                >
                    {disabled ? (
                        <span className="chat-input__spinner"></span>
                    ) : (
                        <svg
                            width="20"
                            height="20"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M2.5 10L17.5 2.5L10 17.5L8.75 11.25L2.5 10Z"
                                fill="currentColor"
                            />
                        </svg>
                    )}
                </button>
            </div>

            <div className="chat-input__hint">
                <span className="chat-input__hint-text">
                    Press Enter to send, Shift+Enter for new line
                </span>
                <span className="chat-input__char-count">
                    {message.length}/2000
                </span>
            </div>
        </form>
    );
};

export default ChatInput;
