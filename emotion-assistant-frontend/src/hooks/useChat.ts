import { useState, useCallback, useRef, useEffect } from 'react';
import { api, isApiError } from '../services/api';
import type { Message } from '../types/api';

interface UseChatReturn {
    messages: Message[];
    isLoading: boolean;
    error: string | null;
    currentEmotion: string | null;
    sendMessage: (content: string, userId: string, userEmail?: string) => Promise<void>;
    clearHistory: (userId: string) => Promise<void>;
    clearError: () => void;
}

export const useChat = (): UseChatReturn => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentEmotion, setCurrentEmotion] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const sendMessage = useCallback(async (
        content: string,
        userId: string,
        userEmail?: string
    ) => {
        setError(null);
        setIsLoading(true);

        // Add user message immediately (optimistic update)
        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);

        try {
            const response = await api.sendMessage({
                message: content,
                user_id: userId,
                user_email: userEmail,
            });

            // Add assistant response
            const assistantMessage: Message = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response.response,
                emotion: response.emotion,
                action: response.action,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            // Update current emotion
            if (response.emotion) {
                setCurrentEmotion(response.emotion);
            }
        } catch (err) {
            const errorMessage = isApiError(err)
                ? `Error: ${err.message}`
                : 'Failed to send message. Please try again.';

            setError(errorMessage);

            // Remove the optimistic user message on error
            setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
        } finally {
            setIsLoading(false);
        }
    }, []);

    const clearHistory = useCallback(async (userId: string) => {
        try {
            await api.clearHistory(userId);
            setMessages([]);
            setCurrentEmotion(null);
            setError(null);
        } catch (err) {
            const errorMessage = isApiError(err)
                ? `Error clearing history: ${err.message}`
                : 'Failed to clear history. Please try again.';
            setError(errorMessage);
        }
    }, []);

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    return {
        messages,
        isLoading,
        error,
        currentEmotion,
        sendMessage,
        clearHistory,
        clearError,
    };
};
