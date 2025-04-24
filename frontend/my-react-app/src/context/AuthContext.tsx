import { createContext, ReactNode, useContext, useState } from "react";

interface AuthContextType {
    accessToken: string | null;
    setTokens: (access: string, refresh: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [accessToken, setAccessToken] = useState<string | null>(null);
    // ... handle refreshToken in state or secure storage

    const setTokens = (access: string, refresh: string) => {
        setAccessToken(access);
        localStorage.setItem("refreshToken", refresh);
    };

    const logout = () => {
        // call /auth/logout endpoint, clear tokens, redirect
        setAccessToken(null);
        localStorage.removeItem("refreshToken");
    };

    return (
        <AuthContext.Provider value={{ accessToken, setTokens, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be inside AuthProvider");
    return ctx;
};