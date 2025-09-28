import { useEffect, useMemo, useState } from "react";
import type { FilterOptions, SearchFilters } from "../lib/api";
import { getFilters } from "../lib/api";

type Props = {
  value: SearchFilters;
  onChange: (v: SearchFilters) => void;
};

export default function SearchFiltersComp({ value, onChange }: Props) {
  const [opts, setOpts] = useState<FilterOptions | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAllSkills, setShowAllSkills] = useState(false);

  useEffect(() => {
    setLoading(true);
    getFilters()
      .then((o) => setOpts(o))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const companies = useMemo(() => opts?.companies ?? [], [opts]);
  const roles = useMemo(() => opts?.roles ?? [], [opts]);
  const locations = useMemo(() => opts?.locations ?? [], [opts]);
  const skills = useMemo(() => opts?.skills ?? [], [opts]);

  const visibleSkills = showAllSkills ? skills : skills.slice(0, 12);

  if (loading) {
    return (
      <div className="flex items-center gap-2" style={{ padding: "var(--space-2) 0" }}>
        <span className="spinner" style={{ width: "16px", height: "16px" }}></span>
        <span className="muted small">Loading filters...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error small">Failed to load filters: {error}</div>
    );
  }

  if (!opts) return null;

  const toggleSkill = (item: string) => {
    const current = new Set(value.skills ?? []);
    if (current.has(item)) {
      current.delete(item);
    } else {
      current.add(item);
    }
    onChange({ ...value, skills: Array.from(current) });
  };

  return (
    <div className="filters-compact">
      {/* Dropdown Filters in Grid */}
      <div className="filter-grid" style={{
        display: "grid",
        gap: "var(--space-2)",
        marginBottom: "var(--space-3)"
      }}>
        <div>
          <label className="label small">Role</label>
          <select
            value={value.role ?? ""}
            onChange={(e) => onChange({ ...value, role: e.target.value || null })}
            style={{ fontSize: "var(--text-sm)", padding: "var(--space-1) var(--space-1)" }}
          >
            <option value="">Any Role</option>
            {roles.map((r) => (
              <option key={r.value} value={r.value}>
                {r.value} ({r.count})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label small">Company</label>
          <select
            value={value.company ?? ""}
            onChange={(e) => onChange({ ...value, company: e.target.value || null })}
            style={{ fontSize: "var(--text-sm)", padding: "var(--space-1) var(--space-1)" }}
          >
            <option value="">Any Company</option>
            {companies.map((c) => (
              <option key={c.value} value={c.value}>
                {c.value} ({c.count})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label small">Location</label>
          <select
            value={value.location ?? ""}
            onChange={(e) => onChange({ ...value, location: e.target.value || null })}
            style={{ fontSize: "var(--text-sm)", padding: "var(--space-1) var(--space-1)" }}
          >
            <option value="">Any Location</option>
            {locations.map((l) => (
              <option key={l.value} value={l.value}>
                {l.value} ({l.count})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label small">Min Experience (years)</label>
          <input
            type="number"
            min={0}
            max={50}
            placeholder="Any"
            value={value.years_experience ?? ""}
            onChange={(e) =>
              onChange({ ...value, years_experience: e.target.value ? Number(e.target.value) : null })
            }
            style={{ fontSize: "var(--text-sm)", padding: "var(--space-1) var(--space-1)" }}
          />
        </div>
      </div>

      {/* Skills Section - Compact */}
      {skills.length > 0 && (
        <div className="mb-3">
          <div className="flex justify-between items-center mb-2">
            <label className="label small">
              Skills
              {value.skills && value.skills.length > 0 && (
                <span className="badge badge-primary" style={{ marginLeft: "var(--space-1)" }}>
                  {value.skills.length}
                </span>
              )}
            </label>
            {skills.length > 12 && (
              <button
                type="button"
                className="text-sm"
                onClick={() => setShowAllSkills(!showAllSkills)}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--blue-600)",
                  cursor: "pointer",
                  padding: 0,
                  fontSize: "var(--text-sm)",
                }}
              >
                {showAllSkills ? "Show Less" : `Show All (${skills.length})`}
              </button>
            )}
          </div>
          <div className="chips" style={{ maxHeight: showAllSkills ? "none" : "72px", overflow: "hidden" }}>
            {visibleSkills.map((s) => {
              const selected = (value.skills ?? []).includes(s.value);
              return (
                <button
                  key={s.value}
                  type="button"
                  className={`chip selectable ${selected ? "selected" : ""}`}
                  onClick={() => toggleSkill(s.value)}
                  title={`${s.value} (${s.count})`}
                  style={{ fontSize: "var(--text-xs)" }}
                >
                  {s.value}
                  <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                    {s.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected Filters Summary */}
      {(value.skills?.length || value.role || value.company || value.location || value.years_experience) && (
        <div
          className="flex items-center gap-2"
          style={{
            marginTop: "var(--space-2)",
            padding: "var(--space-1) 0",
            borderTop: "1px solid var(--gray-200)",
          }}
        >
          <span className="small muted">Active filters:</span>
          <div className="chips">
            {value.role && (
              <span className="chip" style={{ fontSize: "var(--text-xs)" }}>
                Role: {value.role}
                <button
                  type="button"
                  onClick={() => onChange({ ...value, role: null })}
                  style={{
                    marginLeft: "4px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            )}
            {value.company && (
              <span className="chip" style={{ fontSize: "var(--text-xs)" }}>
                Company: {value.company}
                <button
                  type="button"
                  onClick={() => onChange({ ...value, company: null })}
                  style={{
                    marginLeft: "4px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            )}
            {value.location && (
              <span className="chip" style={{ fontSize: "var(--text-xs)" }}>
                Location: {value.location}
                <button
                  type="button"
                  onClick={() => onChange({ ...value, location: null })}
                  style={{
                    marginLeft: "4px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            )}
            {value.years_experience && (
              <span className="chip" style={{ fontSize: "var(--text-xs)" }}>
                Experience: {value.years_experience}+ years
                <button
                  type="button"
                  onClick={() => onChange({ ...value, years_experience: null })}
                  style={{
                    marginLeft: "4px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            )}
            {value.skills?.map((skill) => (
              <span key={skill} className="chip" style={{ fontSize: "var(--text-xs)" }}>
                {skill}
                <button
                  type="button"
                  onClick={() => toggleSkill(skill)}
                  style={{
                    marginLeft: "4px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}