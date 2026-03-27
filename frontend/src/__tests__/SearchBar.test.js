import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchBar from '../SearchBar';

describe('SearchBar', () => {
  it('renders input and button', () => {
    render(<SearchBar onSearch={jest.fn()} loading={false} />);
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeInTheDocument();
  });

  it('input has correct placeholder', () => {
    render(<SearchBar onSearch={jest.fn()} loading={false} />);
    expect(screen.getByTestId('search-input')).toHaveAttribute('placeholder', 'Digite sua pesquisa...');
  });

  it('button is not disabled when loading=false', () => {
    render(<SearchBar onSearch={jest.fn()} loading={false} />);
    expect(screen.getByTestId('search-button')).not.toBeDisabled();
  });

  it('button is disabled when loading=true', () => {
    render(<SearchBar onSearch={jest.fn()} loading={true} />);
    expect(screen.getByTestId('search-button')).toBeDisabled();
  });

  it('typing in input updates value', async () => {
    const user = userEvent.setup();
    render(<SearchBar onSearch={jest.fn()} loading={false} />);
    const input = screen.getByTestId('search-input');
    await user.type(input, 'hello');
    expect(input).toHaveValue('hello');
  });

  it('submitting form calls onSearch with input value', async () => {
    const user = userEvent.setup();
    const onSearch = jest.fn();
    render(<SearchBar onSearch={onSearch} loading={false} />);
    await user.type(screen.getByTestId('search-input'), 'react');
    await user.click(screen.getByTestId('search-button'));
    expect(onSearch).toHaveBeenCalledWith('react');
  });

  it('does not call onSearch if input is empty', async () => {
    const user = userEvent.setup();
    const onSearch = jest.fn();
    render(<SearchBar onSearch={onSearch} loading={false} />);
    await user.click(screen.getByTestId('search-button'));
    expect(onSearch).not.toHaveBeenCalled();
  });

  it('does not call onSearch if input is only whitespace', async () => {
    const user = userEvent.setup();
    const onSearch = jest.fn();
    render(<SearchBar onSearch={onSearch} loading={false} />);
    await user.type(screen.getByTestId('search-input'), '   ');
    await user.click(screen.getByTestId('search-button'));
    expect(onSearch).not.toHaveBeenCalled();
  });
});
