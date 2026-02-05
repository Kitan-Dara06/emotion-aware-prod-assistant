// API Request/Response Types matching backend Pydantic models

export interface ChatRequest {
    message: string;
    user_email?: string;
    user_id?: string;
}

export interface ChatResponse {
    response: string;
    emotion?: string;
    action?: string;
    tool_result?: string;
}

export interface HistoryRequest {
    user_id: string;
    limit?: number;
}

export interface HistoryResponse {
    messages: ConversationMessage[];
    total: number;
}

export interface ConversationMessage {
    id: number;
    session_id: string;
    user_id: string;
    role: 'user' | 'assistant';
    content: string;
    emotion?: string;
    action?: string;
    timestamp: string;
}

export interface HealthResponse {
    status: string;
    service: string;
    version: string;
}

// Frontend-specific types

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    emotion?: string;
    action?: string;
    timestamp: Date;
}

export interface EmotionColor {
    primary: string;
    secondary: string;
    glow: string;
}
