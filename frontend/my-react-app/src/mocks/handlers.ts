import { http, HttpResponse } from "msw";


const API = process.env.REACT_APP_API_URL || '';

export const handlers = [
    http.post(`${API}/auth/register`, async ({ request }) => {
        const { username, email, password } = await request.json() as { username: string; email: string; password: string };

        console.log("Register Request - Username:", username);
        console.log("Register Request - Email:", email);
        console.log("Register Request - Password:", password);

        if (username === "duplicate") {
            return HttpResponse.json(
                {
                    success: false,
                    error_code: "HTTP_ERROR",
                    message: "Username already registered",
                },
                { status: 400 }
            );
        }
        return HttpResponse.json(
            {
                success: true,
                message: "User registered successfully",
                access_token: "fake-access-token",
                refresh_token: "fake-refresh-token"
            },
            { status: 201 }
        );
    }),

    http.post(`${API}/auth/login`, async ({ request }) => {
        const formData = await request.formData();
        const username = formData.get('username') as string;
        const password = formData.get('password') as string;

        if (username !== 'alice' || password !== 'Password123!') {
            return HttpResponse.json(
                {
                    success: false,
                    error_code: "HTTP_ERROR",
                    message: "Invalid username or password",
                },
                { status: 401 }
            );
        }
        return HttpResponse.json({
            access_token: 'fake-jwt-token',
            refresh_token: 'fake-refresh-token',
            token_type: 'bearer',
        });
    }),
];