import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { LoginData, loginSchema } from "../../schemas/auth";
import { useForm } from "react-hook-form";
import { login as loginApi } from "../../services/auth";
import axios, { AxiosError } from "axios";

export default function LoginForm() {
    const { setTokens } = useAuth();
    const navigate = useNavigate();
    const [serverError, setServerError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting }
    } = useForm<LoginData>({
        resolver: zodResolver(loginSchema)
    });

    const onSubmit = async (data: LoginData) => {
        setServerError(null);
        try {
            const response = await loginApi(data);
            const { access_token, refresh_token } = response.data;
            setTokens(access_token, refresh_token);
            navigate("/dashboard"); // Whatever protected route to redirect to
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                const axiosErr = error as AxiosError<{message: string}>;
                setServerError(
                    axiosErr.response?.data?.message || 
                    "Login failed. Please try again."
                );
            } else {
                setServerError("An unexpected error occurred, please try again.");
            }
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {serverError && (
                <div className="text-red-600 text-sm">{serverError}</div>
            )}

            <div>
                <label className="block text-sm font-medium">Username</label>
                <input
                    {...register("username")}
                    className="mt-1 block w-full border rounded p-2"
                />
                {errors.username && (
                    <p className="text-red-600 text-sm">{errors.username.message}</p>
                )}
            </div>

            <div>
                <label className="block text-sm font-medium">Password</label>
                <input
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
                className="w-full py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"            
            >
                {isSubmitting ? "Logging in..." : "Login"}
            </button>
        </form>
    );
}