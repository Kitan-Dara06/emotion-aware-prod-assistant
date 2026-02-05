import type { ChatRequest, ChatResponse, HistoryResponse, HealthResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v2';

function createApiError(status: number, message: string): Error {
    const error = new Error(message);
    error.name = 'ApiError';
    (error as any).status = status;
    return error;
}

function isApiError(error: unknown): error is Error & { status: number } {
    return error instanceof Error && 'status' in error;
}

async function fetchWithErrorHandling<T>(url: string, options?: RequestInit): Promise<T> {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw createApiError(response.status, errorText || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (isApiError(error)) {
            throw error;
        }
        throw createApiError(0, error instanceof Error ? error.message : 'Network error');
    }
}

export const api = {
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        return fetchWithErrorHandling<ChatResponse>(`${API_BASE_URL}/chat`, {
            method: 'POST',
            body: JSON.stringify(request),
        });
    },

    async getHistory(userId: string, limit: number = 10): Promise<HistoryResponse> {
        return fetchWithErrorHandling<HistoryResponse>(`${API_BASE_URL}/history`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, limit }),
        });
    },

    async clearHistory(userId: string): Promise<void> {
        await fetchWithErrorHandling<{ message: string }>(`${API_BASE_URL}/history/${userId}`, {
            method: 'DELETE',
        });
    },

    async getHealth(): Promise<HealthResponse> {
        return fetchWithErrorHandling<HealthResponse>(`${API_BASE_URL}/health`);
    },
};

export { isApiError };
