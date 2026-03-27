import React from 'react';

function Results({ results, loading }) {
  if (loading) {
    return <div data-testid="loading">Carregando...</div>;
  }

  if (!results || results.length === 0) {
    return <div data-testid="no-results">Nenhum resultado encontrado.</div>;
  }

  return (
    <ul data-testid="results-list">
      {results.map((item, index) => (
        <li key={index} data-testid="result-item">
          <a href={item.url} target="_blank" rel="noreferrer">
            {item.title}
          </a>
          <p>{item.snippet}</p>
        </li>
      ))}
    </ul>
  );
}

export default Results;
