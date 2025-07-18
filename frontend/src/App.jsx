import React, { useState } from 'react'
import { ChevronRightIcon, SearchIcon } from '@heroicons/react/outline'

export default function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setResults([])
    try {
      const res = await fetch('http://localhost:8000/retrieve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex flex-col items-center p-8">
      <h1 className="text-4xl font-extrabold text-indigo-700 mb-8">JD Semantic Retriever</h1>

      <div className="w-full max-w-2xl flex">
        <div className="relative flex-grow">
          <SearchIcon className="h-6 w-6 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search job responsibilities..."
            className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="flex items-center justify-center px-6 bg-indigo-600 hover:bg-indigo-700 text-white rounded-r-lg transition disabled:opacity-50"
        >
          {loading ? (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              />
            </svg>
          ) : (
            'Search'
          )}
        </button>
      </div>

      {error && <div className="mt-4 text-red-600">{error}</div>}

      <div className="w-full max-w-2xl mt-8 grid gap-6">
        {results.map(chunk => (
          <div
            key={chunk.chunk_id}
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition"
          >
            <div className="flex justify-between items-center">
              <div>
                <span className="text-lg font-semibold text-indigo-800">
                  JD #{chunk.jd_id}
                </span>
                <span className="ml-2 text-sm text-gray-500">
                  Chunk {chunk.chunk_index}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-600">
                Score: {chunk.score.toFixed(2)}
              </span>
            </div>
            <p className="mt-4 text-gray-700 line-clamp-3">{chunk.text || 'View full chunk below'}</p>
            <a
              href={chunk.object_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center text-indigo-600 hover:underline"
            >
              View Chunk <ChevronRightIcon className="h-4 w-4 ml-1" />
            </a>
          </div>
        ))}
      </div>
    </div>
)
}
