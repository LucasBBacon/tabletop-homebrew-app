import { ReactNode } from "react";

interface AuthLayoutProps {
    title: string;
    children: ReactNode; 
}

export default function AuthLayout({ title, children }: AuthLayoutProps) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full p-6 bg-white shadow-md rounded">
                <h2 className="text-center text-2x1 font-bold mb-4">{title}</h2>
                {children}
            </div>
        </div>
    );
}