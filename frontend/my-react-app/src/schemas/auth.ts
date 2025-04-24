import { z } from "zod";

export const registerSchema = z.object({
    username: z.string().min(3, "Must be at least 3 characters"),
    email:    z.string().email("Invalid email"),
    password: z.string()
               .min(8, "Min 8 chars")
               .regex(/[A-Z]/, "Needs uppercase")
               .regex(/\d/, "Needs a number")
               .regex(/[^A-Za-z0-9]/, "Needs special char"),
});

export const loginSchema = z.object({
    username: z.string().min(1),
    password: z.string().min(1),
});

export type RegisterData = z.infer<typeof registerSchema>;
export type LoginData = z.infer<typeof loginSchema>;