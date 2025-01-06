import './globals.css'

export const metadata = {
  title: 'EcoPrint',
  description: 'Track your sustainable transport activities and calculate your carbon footprint savings.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white">
        {children}
      </body>
    </html>
  )
} 