import React, { useState } from 'react';

function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onSearch(value);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        data-testid="search-input"
        type="text"
        placeholder="Digite sua pesquisa..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button data-testid="search-button" type="submit" disabled={loading}>
        Pesquisar
      </button>
    </form>
  );
}

export default SearchBar;
