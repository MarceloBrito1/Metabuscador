import React from 'react';
import { render, screen } from '@testing-library/react';
import Results from '../Results';

const sampleResults = [
  { title: 'Result One', url: 'https://example.com/1', snippet: 'Snippet one' },
  { title: 'Result Two', url: 'https://example.com/2', snippet: 'Snippet two' },
];

describe('Results', () => {
  it('renders loading indicator when loading=true', () => {
    render(<Results results={[]} loading={true} />);
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
  });

  it('does not show results list when loading=true', () => {
    render(<Results results={sampleResults} loading={true} />);
    expect(screen.queryByTestId('results-list')).not.toBeInTheDocument();
  });

  it('renders no-results when results is empty array', () => {
    render(<Results results={[]} loading={false} />);
    expect(screen.getByTestId('no-results')).toBeInTheDocument();
    expect(screen.getByText('Nenhum resultado encontrado.')).toBeInTheDocument();
  });

  it('renders no-results when results is null', () => {
    render(<Results results={null} loading={false} />);
    expect(screen.getByTestId('no-results')).toBeInTheDocument();
  });

  it('renders results list when results has items', () => {
    render(<Results results={sampleResults} loading={false} />);
    expect(screen.getByTestId('results-list')).toBeInTheDocument();
  });

  it('each result item has title as link with correct href', () => {
    render(<Results results={sampleResults} loading={false} />);
    expect(screen.getByRole('link', { name: 'Result One' })).toHaveAttribute('href', 'https://example.com/1');
    expect(screen.getByRole('link', { name: 'Result Two' })).toHaveAttribute('href', 'https://example.com/2');
  });

  it('each result item shows snippet', () => {
    render(<Results results={sampleResults} loading={false} />);
    expect(screen.getByText('Snippet one')).toBeInTheDocument();
    expect(screen.getByText('Snippet two')).toBeInTheDocument();
  });

  it('link opens in new tab (target="_blank")', () => {
    render(<Results results={sampleResults} loading={false} />);
    const links = screen.getAllByRole('link');
    links.forEach((link) => expect(link).toHaveAttribute('target', '_blank'));
  });

  it('correct number of result items rendered', () => {
    render(<Results results={sampleResults} loading={false} />);
    expect(screen.getAllByTestId('result-item')).toHaveLength(2);
  });
});
