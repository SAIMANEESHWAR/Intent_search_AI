const ShootingSchedule = ({ data }) => {
  const calendar = data?.shooting_calendar || []
  const blocked = data?.blocked_scenes || []
  const suggestions = data?.suggestions || []
  const hasConflicts = blocked.length > 0

  return (
    <div style={{ marginBottom: '32px' }}>
      <h3 style={{ color: 'var(--text)', marginBottom: '20px', fontSize: '1.2rem' }}>
        📅 Shooting Schedule
      </h3>

      {calendar.length === 0 && !hasConflicts && (
        <div
          style={{
            background: '#171717',
            padding: '32px',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border-strong)',
            textAlign: 'center',
            color: 'var(--text-muted)'
          }}
        >
          No shooting calendar was generated. Add actors (name, daily rate, available days) and generate a plan to see the schedule.
        </div>
      )}

      {calendar.length > 0 && (
        <div
          style={{
            overflowX: 'auto',
            marginBottom: '24px',
            border: '1px solid var(--border-strong)',
            borderRadius: 'var(--radius)',
            background: '#171717'
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '400px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-strong)' }}>
                <th style={{ textAlign: 'left', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 600 }}>Scene</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 600 }}>Day range</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 600 }}>Actors</th>
              </tr>
            </thead>
            <tbody>
              {calendar.map((entry, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px 16px', color: 'var(--text)' }}>Scene {entry.scene_number}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text)' }}>
                    Day {entry.start_day} – Day {entry.end_day}
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--text)' }}>
                    {Array.isArray(entry.actors) ? entry.actors.join(', ') : (entry.actors ?? '—')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {hasConflicts && (
        <div
          style={{
            marginTop: '24px',
            padding: '20px',
            borderRadius: 'var(--radius)',
            border: '1px solid #ef4444',
            background: 'rgba(239, 68, 68, 0.08)'
          }}
        >
          <h4 style={{ color: '#ef4444', marginBottom: '12px', fontSize: '1rem' }}>
            ⚠️ Conflict: Scenes that could not be scheduled
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text)' }}>
            {blocked.map((item, idx) => (
              <li key={idx} style={{ marginBottom: '8px' }}>
                <strong>Scene {item.scene_number}</strong>: {item.reason ?? (item.actor_shortage ? `Actor availability: ${item.actor_shortage} (${item.days_missing ?? ''} days missing)` : 'Not enough actor days')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {suggestions.length > 0 && (
        <div
          style={{
            marginTop: '24px',
            padding: '20px',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--primary)',
            background: 'var(--primary-dim)'
          }}
        >
          <h4 style={{ color: 'var(--primary)', marginBottom: '12px', fontSize: '1rem' }}>
            💡 Suggestions
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text)' }}>
            {suggestions.map((text, idx) => (
              <li key={idx} style={{ marginBottom: '6px' }}>{text}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default ShootingSchedule
