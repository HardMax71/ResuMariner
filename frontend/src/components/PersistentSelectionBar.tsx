import { useSelection } from '../contexts/SelectionContext';
import { useNavigate } from 'react-router-dom';
import { X, Users, MessageCircle, Sparkles } from 'lucide-react';

export default function PersistentSelectionBar() {
  const { selected, clearSelection, getSelectedUids } = useSelection();
  const navigate = useNavigate();

  if (selected.length === 0) return null;

  const handleCompare = () => {
    const uids = getSelectedUids();
    navigate(`/rag/compare?uids=${uids.join(',')}`);
    clearSelection();
  };

  const handleInterviews = () => {
    const uid = selected[0].uid;
    navigate(`/rag/interview?uid=${uid}`);
    clearSelection();
  };

  const handleExplainMatch = () => {
    const uid = selected[0].uid;
    navigate(`/rag/explain-match?uid=${uid}`);
    clearSelection();
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 999,
        background: 'rgba(12, 10, 9, 0.98)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderTop: '1px solid rgba(129, 140, 248, 0.3)',
        padding: 'var(--space-3) var(--space-4)',
        boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.4)',
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-3)',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '16px',
              fontWeight: 700,
              color: '#818cf8',
            }}
          >
            {selected.length} Selected
          </span>
          <div
            style={{
              fontSize: '13px',
              color: '#a8a29e',
              maxWidth: '300px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {selected.map(c => c.name).join(', ')}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)', marginLeft: 'auto', flexWrap: 'wrap' }}>
          {selected.length >= 2 && (
            <button
              onClick={handleCompare}
              className="btn"
              style={{
                background: 'var(--primary-600)',
                color: 'white',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-1)',
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: 600,
              }}
            >
              <Users size={16} />
              Compare
            </button>
          )}

          {selected.length === 1 && (
            <>
              <button
                onClick={handleExplainMatch}
                className="btn"
                style={{
                  background: 'var(--accent1-600)',
                  color: 'white',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-1)',
                  padding: '8px 16px',
                  fontSize: '14px',
                  fontWeight: 600,
                }}
              >
                <Sparkles size={16} />
                Explain Match
              </button>

              <button
                onClick={handleInterviews}
                className="btn"
                style={{
                  background: 'var(--accent2-600)',
                  color: 'white',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-1)',
                  padding: '8px 16px',
                  fontSize: '14px',
                  fontWeight: 600,
                }}
              >
                <MessageCircle size={16} />
                Interview
              </button>
            </>
          )}

          <button
            onClick={clearSelection}
            className="btn"
            style={{
              background: 'transparent',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-1)',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: 600,
            }}
          >
            <X size={16} />
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}
