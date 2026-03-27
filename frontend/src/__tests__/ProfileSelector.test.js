import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfileSelector from '../ProfileSelector';

describe('ProfileSelector', () => {
  it('renders label "Perfil:"', () => {
    render(<ProfileSelector profile="general" onChange={jest.fn()} />);
    expect(screen.getByText('Perfil:')).toBeInTheDocument();
  });

  it('renders all 4 options', () => {
    render(<ProfileSelector profile="general" onChange={jest.fn()} />);
    expect(screen.getByRole('option', { name: /Geral/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Científico/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Jornalístico/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Compras/i })).toBeInTheDocument();
  });

  it('has the current profile selected by default', () => {
    render(<ProfileSelector profile="scientific" onChange={jest.fn()} />);
    expect(screen.getByTestId('profile-selector')).toHaveValue('scientific');
  });

  it('calls onChange when selection changes', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    render(<ProfileSelector profile="general" onChange={onChange} />);
    await user.selectOptions(screen.getByTestId('profile-selector'), 'shopping');
    expect(onChange).toHaveBeenCalledWith('shopping');
  });

  it('has correct data-testid', () => {
    render(<ProfileSelector profile="general" onChange={jest.fn()} />);
    expect(screen.getByTestId('profile-selector')).toBeInTheDocument();
  });
});
