// frontend/my-react-app/src/components/auth/RegisterForm.tsx

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { RegisterData, registerSchema } from "../../schemas/auth";
import { register as registerApi } from "../../services/auth";
import { AxiosError } from "axios";

export default function RegisterForm() {
    const { setTokens } = useAuth();
    const navigate = useNavigate();
    const [serverError, setServerError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<RegisterData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterData) => {
        setServerError(null);
        try {
            const response = await registerApi(data);
            // Optionally auto-login the user after registration
            const { access_token, refresh_token } = response.data;
            setTokens(access_token, refresh_token);
            navigate("/auth/login");
        } catch (error: unknown) {
            if ((error as AxiosError).isAxiosError) {
                // Zod won't run here, backend validation errors
                const axiosErr = error as AxiosError<{ message: string }>;
                console.error("Registration error:", axiosErr.response?.data);
                setServerError(axiosErr.response?.data?.message || "Registration failed. Please try again.");
            } else {
                setServerError("An unexpected error occured, please try again.");
            }
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {serverError && (
                <div className="text-red-600 text-sm">{serverError}</div>
            )}

            <div>
                <label htmlFor="username" className="block text-sm font-medium">Username</label>
                <input
                    id="username"
                    {...register("username")}
                    className="mt-1 block w-full border rounded p-2"
                />
                {errors.username && (
                    <p className="text-red-600 text-sm">{errors.username.message}</p>
                )}
            </div>

            <div>
                <label htmlFor="email" className="block text-sm font-medium">Email</label>
                <input
                    id="email"
                    {...register("email")}
                    className="mt-1 block w-full border rounded p-2"
                />
                {errors.email && (
                    <p className="text-red-600 text-sm">{errors.email.message}</p>
                )}
            </div>

            <div>
                <label htmlFor="password" className="block text-sm font-medium">Password</label>
                <input
                    id="password"
                    type="password"
                    {...register("password")}
                    className="mt-1 block w-full border rounded p-2"
                />
                {errors.password && (
                    <p className="text-red-600 text-sm">{errors.password.message}</p>
                )}
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
                {isSubmitting ? "Registering..." : "Register"}
            </button>
        </form>
    );
}