'use client'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">EcoPrint</h1>
      <p className="text-xl mb-8">Track your sustainable transport activities and calculate your carbon footprint savings.</p>
      <a
        href="/api/auth/strava"
        className="bg-[#FC4C02] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#E34402] transition-colors"
      >
        Connect with Strava
      </a>
    </main>
  )
} 