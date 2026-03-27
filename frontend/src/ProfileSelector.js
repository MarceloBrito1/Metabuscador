import React from 'react';

function ProfileSelector({ profile, onChange }) {
  return (
    <div>
      <label htmlFor="profile-selector">Perfil:</label>
      <select
        id="profile-selector"
        data-testid="profile-selector"
        value={profile}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="general">🌐 Geral</option>
        <option value="scientific">🔬 Científico</option>
        <option value="journalistic">📰 Jornalístico</option>
        <option value="shopping">🛒 Compras</option>
      </select>
    </div>
  );
}

export default ProfileSelector;
