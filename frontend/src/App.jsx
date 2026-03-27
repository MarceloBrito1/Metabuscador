import { useState } from 'react'

const API_BASE = '/api'

const PROFILES = [
  { id: 'general', label: 'Geral' },
  { id: 'scientific', label: 'Científico 🔬' },
  { id: 'journalistic', label: 'Jornalístico 📰' },
  { id: 'shopping', label: 'Compras 🛒' },
]

const SOURCE_COLORS = {
  bing: 'bg-blue-100 text-blue-800',
  duckduckgo: 'bg-orange-100 text-orange-800',
  google: 'bg-green-100 text-green-800',
}

function SourceBadge({ source }) {
  const cls = SOURCE_COLORS[source] || 'bg-gray-100 text-gray-700'
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}>
      {source}
    </span>
  )
}

function ResultCard({ result }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-1">
        <a
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-700 font-semibold text-base hover:underline leading-tight"
        >
          {result.title || result.url}
        </a>
        <SourceBadge source={result.source} />
      </div>
      <p className="text-xs text-gray-500 truncate mb-2">{result.url}</p>
      {result.snippet && (
        <p className="text-sm text-gray-700 line-clamp-3">{result.snippet}</p>
      )}
    </div>
  )
}

function LimitBar({ remaining, total }) {
  const pct = Math.round((remaining / total) * 100)
  const color =
    pct > 50 ? 'bg-green-500' : pct > 20 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-600 whitespace-nowrap">
        {remaining}/{total} buscas restantes hoje
      </span>
    </div>
  )
}

export default function App() {
  const [query, setQuery] = useState('')
  const [profile, setProfile] = useState('general')
  const [userId] = useState(() => {
    let id = localStorage.getItem('metabuscador_user_id')
    if (!id) {
      id = 'user_' + Math.random().toString(36).slice(2, 10)
      localStorage.setItem('metabuscador_user_id', id)
    }
    return id
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [response, setResponse] = useState(null)

  async function handleSearch(e) {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          profile,
          user_id: userId,
          results_per_engine: 10,
        }),
      })

      if (res.status === 429) {
        const data = await res.json()
        setError(data.detail || 'Limite diário atingido.')
        return
      }

      if (!res.ok) {
        throw new Error(`Erro ${res.status}: ${res.statusText}`)
      }

      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err.message || 'Ocorreu um erro inesperado.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-10 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-800 tracking-tight">
            🔍 Metabuscador Limpo
          </h1>
          <p className="text-gray-500 mt-2 text-sm">
            Resultados de múltiplos motores · sem anúncios · sem duplicatas
          </p>
        </header>

        {/* Search form */}
        <form onSubmit={handleSearch} className="bg-white rounded-2xl shadow-md p-5 mb-6">
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="O que você está buscando?"
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Buscando…' : 'Buscar'}
            </button>
          </div>

          {/* Profile selector */}
          <div className="flex gap-2 flex-wrap">
            {PROFILES.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setProfile(p.id)}
                className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                  profile === p.id
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </form>

        {/* Rate limit bar */}
        {response && (
          <div className="mb-4 px-1">
            <LimitBar remaining={response.remaining_searches} total={100} />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-xl px-4 py-3 text-sm mb-4">
            ⚠️ {error}
          </div>
        )}

        {/* Results */}
        {response && (
          <div>
            <div className="flex items-center justify-between mb-3 px-1">
              <span className="text-sm text-gray-600">
                <strong>{response.total}</strong> resultado
                {response.total !== 1 ? 's' : ''} · perfil:{' '}
                <span className="font-medium">{response.profile_label}</span>
              </span>
              <div className="flex gap-1">
                {response.engines_used.map((e) => (
                  <SourceBadge key={e} source={e} />
                ))}
              </div>
            </div>

            {response.results.length === 0 ? (
              <p className="text-center text-gray-500 py-10 text-sm">
                Nenhum resultado encontrado. Tente outros termos.
              </p>
            ) : (
              <div className="flex flex-col gap-3">
                {response.results.map((r, i) => (
                  <ResultCard key={i} result={r} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
