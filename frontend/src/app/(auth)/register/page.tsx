"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mic, Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    company_name: "",
    company_slug: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
      ...(name === "company_name"
        ? { company_slug: value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") }
        : {}),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await register(form);
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  const fields = [
    { name: "full_name", label: "Full Name", type: "text", placeholder: "John Doe" },
    { name: "email", label: "Email", type: "email", placeholder: "john@company.com" },
    { name: "password", label: "Password", type: "password", placeholder: "Min. 8 characters" },
    { name: "company_name", label: "Company Name", type: "text", placeholder: "Acme Inc." },
    { name: "company_slug", label: "Company URL Slug", type: "text", placeholder: "acme-inc" },
  ];

  return (
    <div className="min-h-screen mesh-gradient flex items-center justify-center p-4">
      <motion.div
        className="fixed top-10 right-32 w-80 h-80 rounded-full bg-[hsl(var(--secondary)/0.07)] blur-3xl"
        animate={{ x: [0, -40, 0], y: [0, 30, 0] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        <div className="glass rounded-2xl p-8 shadow-2xl">
          <div className="flex flex-col items-center mb-8">
            <motion.div
              className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center mb-4 glow-primary"
              whileHover={{ scale: 1.05, rotate: -5 }}
            >
              <Mic className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-2xl font-bold font-[family-name:var(--font-outfit)] gradient-text">
              Create Account
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
              Set up your AI sales agent in minutes
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-[hsl(var(--destructive)/0.1)] border border-[hsl(var(--destructive)/0.3)] text-[hsl(var(--destructive))] px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            {fields.map((field) => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1.5">
                  {field.label}
                </label>
                <input
                  type={field.type}
                  name={field.name}
                  value={form[field.name as keyof typeof form]}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-xl bg-[hsl(var(--muted)/0.5)] border border-[hsl(var(--border))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary)/0.5)] focus:border-transparent transition-all text-sm"
                  placeholder={field.placeholder}
                  required
                  minLength={field.name === "password" ? 8 : undefined}
                />
              </div>
            ))}

            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-[hsl(var(--primary))] to-[hsl(var(--secondary))] text-white font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2 glow-primary mt-2"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Account"}
            </motion.button>
          </form>

          <p className="text-center text-sm text-[hsl(var(--muted-foreground))] mt-6">
            Already have an account?{" "}
            <a href="/login" className="text-[hsl(var(--primary))] hover:underline font-medium">
              Sign in
            </a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
