import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface AppContextType {
    userId: string;
    userEmail: string | null;
    setUserEmail: (email: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppContext = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within AppProvider');
    }
    return context;
};

interface AppProviderProps {
    children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
    const [userId, setUserId] = useState<string>('');
    const [userEmail, setUserEmail] = useState<string | null>(null);

    useEffect(() => {
        // Get or create user ID from localStorage
        let storedUserId = localStorage.getItem('emotion-assistant-user-id');

        if (!storedUserId) {
            storedUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('emotion-assistant-user-id', storedUserId);
        }

        setUserId(storedUserId);

        // Get user email if stored
        const storedEmail = localStorage.getItem('emotion-assistant-user-email');
        if (storedEmail) {
            setUserEmail(storedEmail);
        }
    }, []);

    const handleSetUserEmail = (email: string | null) => {
        setUserEmail(email);
        if (email) {
            localStorage.setItem('emotion-assistant-user-email', email);
        } else {
            localStorage.removeItem('emotion-assistant-user-email');
        }
    };

    return (
        <AppContext.Provider value={{ userId, userEmail, setUserEmail: handleSetUserEmail }}>
            {children}
        </AppContext.Provider>
    );
};
