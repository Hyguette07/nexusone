"use client";

import { DisclaimerBanner } from "@/components/Disclaimer";
import { homeFor, useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setPending(true);
    try {
      const user = await register({ email, password, full_name: fullName, phone: phone || undefined });
      router.push(homeFor(user.role));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
      <p className="text-xs uppercase tracking-[0.3em] text-signal">Citizen register</p>
      <h1 className="mt-2 font-display text-5xl uppercase">Report as a neighbour</h1>
      <div className="mt-4">
        <DisclaimerBanner compact />
      </div>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <label className="block text-sm text-ash">
          Full name
          <input className="mt-1 w-full rounded-md px-3 py-2" required minLength={2} value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </label>
        <label className="block text-sm text-ash">
          Email
          <input className="mt-1 w-full rounded-md px-3 py-2" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="block text-sm text-ash">
          Phone (optional)
          <input className="mt-1 w-full rounded-md px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        <label className="block text-sm text-ash">
          Password
          <input className="mt-1 w-full rounded-md px-3 py-2" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error ? <p className="text-sm text-crit">{error}</p> : null}
        <button disabled={pending} className="w-full rounded-md bg-signal py-3 text-charcoal disabled:opacity-60">
          {pending ? "Creating…" : "Create citizen account"}
        </button>
      </form>
      <p className="mt-4 text-sm text-ash">
        Already on the desk? <Link className="text-signal underline" href="/login">Sign in</Link>
      </p>
    </main>
  );
}
