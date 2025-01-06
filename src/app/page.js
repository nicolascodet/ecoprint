'use client'

import { useEffect, useState } from 'react'

export default function Home() {
  const [apiUrl, setApiUrl] = useState('')

  useEffect(() => {
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || '')
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">EcoPrint</h1>
      <p className="text-xl mb-8">Track your sustainable transport activities and calculate your carbon footprint savings.</p>
      <a
        href={apiUrl ? `${apiUrl}/api/auth/strava` : '#'}
        className="bg-[#FC4C02] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#E34402] transition-colors"
        onClick={(e) => !apiUrl && e.preventDefault()}
      >
        Connect with Strava
      </a>
    </main>
  )
} 