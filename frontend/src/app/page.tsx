import { DisclaimerBanner } from "@/components/Disclaimer";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
      <p className="text-xs uppercase tracking-[0.35em] text-signal">Hyguette Labs · NexusOne</p>
      <h1 className="mt-4 max-w-3xl font-display text-5xl uppercase leading-[0.95] md:text-7xl">
        One board. Four emergencies. The city does not wait.
      </h1>
      <p className="mt-6 max-w-xl text-lg text-ash">
        Real-time dispatch for flood, medical, fire, and missing-person reports. DispatchRanker
        scores which clinic, bus, shelter, or volunteer team should move — by distance, type, capacity,
        and whether they are already busy.
      </p>
      <div className="mt-8 max-w-xl">
        <DisclaimerBanner />
      </div>
      <div className="mt-10 flex flex-wrap gap-4">
        <Link href="/login" className="rounded-md bg-signal px-6 py-3 font-medium text-charcoal">
          Open the dispatch desk
        </Link>
        <Link href="/register" className="rounded-md border border-white/20 px-6 py-3">
          Register as a citizen
        </Link>
      </div>
      <p className="mt-16 text-sm text-ash">
        Demo: dispatcher@nexusone.local · password from APP_SEED_PASSWORD (default ChangeMe123!)
      </p>
    </main>
  );
}
