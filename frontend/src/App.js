import React, { useState } from 'react';
import ProfileSelector from './ProfileSelector';
import SearchBar from './SearchBar';
import Results from './Results';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState('general');

  const handleSearch = async (query) => {
    if (!query || !query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/search?q=${encodeURIComponent(query)}&profile=${profile}`);
      const data = await res.json();
      setResults(data.results);
    } catch (err) {
      setError('Erro ao realizar a busca. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 data-testid="app-title">Metabuscador Limpo 🔍</h1>
      <ProfileSelector profile={profile} onChange={setProfile} />
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <p data-testid="error-message">{error}</p>}
      <Results results={results} loading={loading} />
    </div>
  );
}

export default App;
