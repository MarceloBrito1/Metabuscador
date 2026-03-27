import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

describe('App', () => {
  it('renders title "Metabuscador Limpo 🔍"', () => {
    render(<App />);
    expect(screen.getByTestId('app-title')).toHaveTextContent('Metabuscador Limpo 🔍');
  });

  it('renders SearchBar', () => {
    render(<App />);
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeInTheDocument();
  });

  it('renders ProfileSelector', () => {
    render(<App />);
    expect(screen.getByTestId('profile-selector')).toBeInTheDocument();
  });

  it('Results shows no-results initially', () => {
    render(<App />);
    expect(screen.getByTestId('no-results')).toBeInTheDocument();
  });

  it('handleSearch does nothing if query is empty', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByTestId('search-button'));
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('handleSearch shows loading then results on success', async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      json: async () => ({
        results: [
          { title: 'Test Title', url: 'https://test.com', snippet: 'Test snippet' },
        ],
      }),
    });

    render(<App />);
    await user.type(screen.getByTestId('search-input'), 'react');
    await user.click(screen.getByTestId('search-button'));

    await waitFor(() => {
      expect(screen.getByTestId('results-list')).toBeInTheDocument();
    });
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('handleSearch shows error message on fetch failure', async () => {
    const user = userEvent.setup();
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<App />);
    await user.type(screen.getByTestId('search-input'), 'react');
    await user.click(screen.getByTestId('search-button'));

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });
    expect(screen.getByTestId('error-message')).toHaveTextContent(
      'Erro ao realizar a busca. Tente novamente.'
    );
  });

  it('profile change updates state', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.selectOptions(screen.getByTestId('profile-selector'), 'scientific');
    expect(screen.getByTestId('profile-selector')).toHaveValue('scientific');
  });

  it('search sends correct profile in URL', async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      json: async () => ({ results: [] }),
    });

    render(<App />);
    await user.selectOptions(screen.getByTestId('profile-selector'), 'journalistic');
    await user.type(screen.getByTestId('search-input'), 'news');
    await user.click(screen.getByTestId('search-button'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('profile=journalistic')
      );
    });
  });

  it('loading state is managed correctly', async () => {
    const user = userEvent.setup();
    let resolveFetch;
    global.fetch.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveFetch = resolve;
      })
    );

    render(<App />);
    await user.type(screen.getByTestId('search-input'), 'test');
    await user.click(screen.getByTestId('search-button'));

    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeDisabled();

    resolveFetch({ json: async () => ({ results: [] }) });

    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
    expect(screen.getByTestId('search-button')).not.toBeDisabled();
  });
});
