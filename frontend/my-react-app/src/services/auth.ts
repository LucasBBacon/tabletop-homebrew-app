import axios from "axios";
import type { TokenPair, Token, RegisterData, LoginData } from "../schemas/auth";

export const register = (data: RegisterData) =>
    axios.post("/auth/register", data);

export const login = (data: LoginData) => 
    axios.post<TokenPair>("/auth/login", new URLSearchParams(data));

export const refresh = (refreshToken: string) =>
    axios.post<Token>("/auth/refresh-token", { refresh_token: refreshToken });

export const logout = (accessToken: string, refreshToken?: string) =>
    axios.post(
        "/auth/logout",
        { refresh_token: refreshToken },
        { headers: { Authorization: 'Bearer ${accessToken}' } }
    );