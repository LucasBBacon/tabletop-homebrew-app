import { MemoryRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import RegisterForm from "./RegisterForm";
import { AuthProvider } from "../../context/AuthContext";
import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";


const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

describe("RegisterForm", () => {
    it("renders the form and shows validation errors", async () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <RegisterForm/>
                </AuthProvider>
            </MemoryRouter>
        );

        // Try submiting empty form
        userEvent.click(screen.getByRole("button", { name: /register/i }));
        // expect(await screen.findAllByText(/required|must/i)).toHaveLength(3);
        expect(await screen.findByText("Must be at least 3 characters")).toBeInTheDocument();
        expect(await screen.findByText("Invalid email")).toBeInTheDocument();
        expect(await screen.findByText("Min 8 chars")).toBeInTheDocument();
    });

    it("displays server error on duplicate username", async () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <RegisterForm/>
                </AuthProvider>
            </MemoryRouter>
        );

        const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
        const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
        const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

        // Fill in fields
        await userEvent.type(usernameInput, "duplicate");
        // expect(screen.getByLabelText(/username/i)).toHaveValue("duplicate");
        await userEvent.type(emailInput, "duplicate@test.com");
        // expect(screen.getByLabelText(/email/i)).toHaveValue("duplicate@test.com");
        await userEvent.type(passwordInput, "Passworddddddd123!");
        // expect(screen.getByLabelText(/password/i)).toHaveValue("Passworddddddd123!");
        
        userEvent.click(screen.getByRole("button", { name: /register/i }));

        // wait for server error to appear
        expect(
            await screen.findByText("Username already registered")
        ).toBeInTheDocument();
    });

    it("navigates to login on sucessful registration", async () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <RegisterForm/>
                </AuthProvider>
            </MemoryRouter>
        );

        const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
        const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
        const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

        await userEvent.type(usernameInput, "alice");
        await userEvent.type(emailInput, "alice@test.com");
        await userEvent.type(passwordInput, "Password123!");

        userEvent.click(screen.getByRole("button", { name: /register/i }));

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith("/auth/login");
        });
    });
});