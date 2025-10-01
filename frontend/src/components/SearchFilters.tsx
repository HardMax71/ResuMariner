import { useEffect, useMemo, useState } from "react";
import type {
  FilterOptions,
  SearchFilters,
  LanguageRequirement,
  LocationRequirement,
  EducationRequirement
} from "../lib/api";
import { getFilters } from "../lib/api";
import Badge from "./Badge";
import Chip from "./Chip";

const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

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
  const countries = useMemo(() => opts?.countries ?? [], [opts]);
  const skills = useMemo(() => opts?.skills ?? [], [opts]);
  const educationLevels = useMemo(() => opts?.education_levels ?? [], [opts]);
  const languages = useMemo(() => opts?.languages ?? [], [opts]);

  const visibleSkills = showAllSkills ? skills : skills.slice(0, 12);

  const [expandedLanguage, setExpandedLanguage] = useState<string | null>(null);
  const [expandedCountry, setExpandedCountry] = useState<string | null>(null);
  const [expandedEducationLevel, setExpandedEducationLevel] = useState<string | null>(null);

  // Close expanded selectors on outside click
  useEffect(() => {
    const handleClickOutside = () => {
      setExpandedLanguage(null);
      setExpandedCountry(null);
      setExpandedEducationLevel(null);
    };
    if (expandedLanguage || expandedCountry || expandedEducationLevel) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [expandedLanguage, expandedCountry, expandedEducationLevel]);

  const toggleLanguage = (language: string, level: string) => {
    const current = value.languages ?? [];
    const existing = current.find(l => l.language === language);

    if (existing) {
      // Update level or remove if same level clicked
      if (existing.min_cefr === level) {
        onChange({
          ...value,
          languages: current.filter(l => l.language !== language)
        });
      } else {
        onChange({
          ...value,
          languages: current.map(l =>
            l.language === language ? { ...l, min_cefr: level } : l
          )
        });
      }
    } else {
      // Add new language requirement
      onChange({
        ...value,
        languages: [...current, { language, min_cefr: level }]
      });
    }
    setExpandedLanguage(null);
  };

  const removeLanguageRequirement = (language: string) => {
    const current = value.languages ?? [];
    onChange({
      ...value,
      languages: current.filter(l => l.language !== language)
    });
  };

  const toggleCountry = (country: string, cities: string[]) => {
    const current = value.locations ?? [];
    const existing = current.find(l => l.country === country);

    if (existing) {
      // If same selection, remove it; otherwise update cities
      const sameCitiesSelected = JSON.stringify(existing.cities?.sort()) === JSON.stringify(cities.sort());
      if (sameCitiesSelected) {
        onChange({
          ...value,
          locations: current.filter(l => l.country !== country)
        });
      } else {
        onChange({
          ...value,
          locations: current.map(l =>
            l.country === country ? { ...l, cities: cities.length === 0 ? null : cities } : l
          )
        });
      }
    } else {
      // Add new location requirement
      onChange({
        ...value,
        locations: [...current, { country, cities: cities.length === 0 ? null : cities }]
      });
    }
    setExpandedCountry(null);
  };

  const removeLocationRequirement = (country: string) => {
    const current = value.locations ?? [];
    onChange({
      ...value,
      locations: current.filter(l => l.country !== country)
    });
  };

  const toggleEducationLevel = (level: string, statuses: string[]) => {
    const current = value.education ?? [];
    const existing = current.find(e => e.level === level);

    if (existing) {
      // If same selection, remove it; otherwise update statuses
      const sameStatusesSelected = JSON.stringify(existing.statuses?.sort()) === JSON.stringify(statuses.sort());
      if (sameStatusesSelected) {
        onChange({
          ...value,
          education: current.filter(e => e.level !== level)
        });
      } else {
        onChange({
          ...value,
          education: current.map(e =>
            e.level === level ? { ...e, statuses: statuses.length === 0 ? null : statuses } : e
          )
        });
      }
    } else {
      // Add new education requirement
      onChange({
        ...value,
        education: [...current, { level, statuses: statuses.length === 0 ? null : statuses }]
      });
    }
    setExpandedEducationLevel(null);
  };

  const removeEducationRequirement = (level: string) => {
    const current = value.education ?? [];
    onChange({
      ...value,
      education: current.filter(e => e.level !== level)
    });
  };

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
      <div className="filter-grid" style={{ marginBottom: "var(--space-3)" }}>
        <div>
          <label className="label small">Role</label>
          <select
            value={value.role ?? ""}
            onChange={(e) => onChange({ ...value, role: e.target.value || null })}
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
          />
        </div>
      </div>

      {/* Countries Section - Chip Based */}
      {countries.length > 0 && (
        <div className="mb-3">
          <label className="label small">
            Location
            {value.locations && value.locations.length > 0 && (
              <Badge style={{ marginLeft: "var(--space-1)" }}>
                {value.locations.length}
              </Badge>
            )}
          </label>
          <div className="chips">
            {countries.map((countryOption) => {
              const selected = value.locations?.find(l => l.country === countryOption.country);
              const isExpanded = expandedCountry === countryOption.country;

              return (
                <div key={countryOption.country} style={{ position: "relative", display: "inline-block" }}>
                  <Chip
                    selectable
                    selected={!!selected}
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedCountry(isExpanded ? null : countryOption.country);
                    }}
                    title={`${countryOption.country} (${countryOption.resume_count})`}
                    style={{ fontSize: "var(--text-xs)" }}
                  >
                    {selected
                      ? `${countryOption.country}${selected.cities && selected.cities.length > 0 ? `: ${selected.cities.length} cities` : ': Any'}`
                      : countryOption.country}
                    <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                      {countryOption.resume_count}
                    </span>
                  </Chip>

                  {/* City Selector Popup */}
                  {isExpanded && (
                    <div
                      style={{
                        position: "absolute",
                        top: "calc(100% + 4px)",
                        left: 0,
                        zIndex: 10,
                        background: "white",
                        border: "1px solid var(--gray-300)",
                        borderRadius: "var(--radius-sm)",
                        padding: "var(--space-2)",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                        minWidth: "250px",
                        maxWidth: "350px",
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div style={{ marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--text-sm)" }}>
                        Select cities in {countryOption.country}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px", maxHeight: "200px", overflowY: "auto" }}>
                        <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", padding: "4px" }}>
                          <input
                            type="checkbox"
                            checked={!selected?.cities || selected.cities.length === 0}
                            onChange={() => toggleCountry(countryOption.country, [])}
                          />
                          <span style={{ fontSize: "var(--text-sm)" }}>Any City</span>
                        </label>
                        {countryOption.cities.map(city => {
                          const currentCities = selected?.cities ?? [];
                          const isChecked = currentCities.includes(city);

                          return (
                            <label key={city} style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", padding: "4px" }}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => {
                                  const newCities = isChecked
                                    ? currentCities.filter(c => c !== city)
                                    : [...currentCities, city];
                                  toggleCountry(countryOption.country, newCities);
                                }}
                              />
                              <span style={{ fontSize: "var(--text-sm)" }}>{city}</span>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Education Levels Section - Chip Based */}
      {educationLevels.length > 0 && (
        <div className="mb-3">
          <label className="label small">
            Education
            {value.education && value.education.length > 0 && (
              <Badge style={{ marginLeft: "var(--space-1)" }}>
                {value.education.length}
              </Badge>
            )}
          </label>
          <div className="chips">
            {educationLevels.map((levelOption) => {
              const selected = value.education?.find(e => e.level === levelOption.level);
              const isExpanded = expandedEducationLevel === levelOption.level;

              return (
                <div key={levelOption.level} style={{ position: "relative", display: "inline-block" }}>
                  <Chip
                    selectable
                    selected={!!selected}
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedEducationLevel(isExpanded ? null : levelOption.level);
                    }}
                    title={`${levelOption.level} (${levelOption.resume_count})`}
                    style={{ fontSize: "var(--text-xs)" }}
                  >
                    {selected
                      ? `${levelOption.level}${selected.statuses && selected.statuses.length > 0 ? `: ${selected.statuses.join(', ')}` : ': Any'}`
                      : levelOption.level}
                    <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                      {levelOption.resume_count}
                    </span>
                  </Chip>

                  {/* Status Selector Popup */}
                  {isExpanded && (
                    <div
                      style={{
                        position: "absolute",
                        top: "calc(100% + 4px)",
                        left: 0,
                        zIndex: 10,
                        background: "white",
                        border: "1px solid var(--gray-300)",
                        borderRadius: "var(--radius-sm)",
                        padding: "var(--space-2)",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                        minWidth: "200px",
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div style={{ marginBottom: "var(--space-1)", fontWeight: 600, fontSize: "var(--text-sm)" }}>
                        Select status for {levelOption.level}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", padding: "4px" }}>
                          <input
                            type="checkbox"
                            checked={!selected?.statuses || selected.statuses.length === 0}
                            onChange={() => toggleEducationLevel(levelOption.level, [])}
                          />
                          <span style={{ fontSize: "var(--text-sm)" }}>Any Status</span>
                        </label>
                        {levelOption.statuses.map(status => {
                          const currentStatuses = selected?.statuses ?? [];
                          const isChecked = currentStatuses.includes(status);

                          return (
                            <label key={status} style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", padding: "4px" }}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => {
                                  const newStatuses = isChecked
                                    ? currentStatuses.filter(s => s !== status)
                                    : [...currentStatuses, status];
                                  toggleEducationLevel(levelOption.level, newStatuses);
                                }}
                              />
                              <span style={{ fontSize: "var(--text-sm)" }}>{status}</span>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Languages Section - Chip Based */}
      {languages.length > 0 && (
        <div className="mb-3">
          <label className="label small">
            Languages
            {value.languages && value.languages.length > 0 && (
              <Badge style={{ marginLeft: "var(--space-1)" }}>
                {value.languages.length}
              </Badge>
            )}
          </label>
          <div className="chips">
            {languages.map((langOption) => {
              const selected = value.languages?.find(l => l.language === langOption.language);
              const isExpanded = expandedLanguage === langOption.language;

              return (
                <div key={langOption.language} style={{ position: "relative", display: "inline-block" }}>
                  <Chip
                    selectable
                    selected={!!selected}
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedLanguage(isExpanded ? null : langOption.language);
                    }}
                    title={`${langOption.language} (${langOption.resume_count})`}
                    style={{ fontSize: "var(--text-xs)" }}
                  >
                    {selected ? `${langOption.language}: ${selected.min_cefr}+` : langOption.language}
                    <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                      {langOption.resume_count}
                    </span>
                  </Chip>

                  {/* CEFR Level Selector Popup */}
                  {isExpanded && (
                    <div
                      style={{
                        position: "absolute",
                        top: "calc(100% + 4px)",
                        left: 0,
                        zIndex: 10,
                        background: "white",
                        border: "1px solid var(--gray-300)",
                        borderRadius: "var(--radius-sm)",
                        padding: "var(--space-1)",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                        display: "flex",
                        gap: "4px",
                        minWidth: "200px",
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {CEFR_LEVELS.map(level => (
                        <button
                          key={level}
                          type="button"
                          onClick={() => toggleLanguage(langOption.language, level)}
                          style={{
                            flex: 1,
                            padding: "var(--space-1)",
                            fontSize: "var(--text-xs)",
                            border: `1px solid ${selected?.min_cefr === level ? "var(--blue-600)" : "var(--gray-300)"}`,
                            background: selected?.min_cefr === level ? "var(--blue-50)" : "white",
                            color: selected?.min_cefr === level ? "var(--blue-700)" : "var(--gray-700)",
                            borderRadius: "var(--radius-sm)",
                            cursor: "pointer",
                            fontWeight: selected?.min_cefr === level ? 600 : 400,
                          }}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Skills Section - Compact */}
      {skills.length > 0 && (
        <div className="mb-3">
          <div className="flex justify-between items-center mb-2">
            <label className="label small">
              Skills
              {value.skills && value.skills.length > 0 && (
                <Badge style={{ marginLeft: "var(--space-1)" }}>
                  {value.skills.length}
                </Badge>
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
                <Chip
                  key={s.value}
                  selectable
                  selected={selected}
                  onClick={() => toggleSkill(s.value)}
                  title={`${s.value} (${s.count})`}
                  style={{ fontSize: "var(--text-xs)" }}
                >
                  {s.value}
                  <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                    {s.count}
                  </span>
                </Chip>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected Filters Summary */}
      {(value.skills?.length || value.role || value.company || value.locations?.length || value.years_experience || value.education?.length || value.languages?.length) && (
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
              <Chip
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => onChange({ ...value, role: null })}
              >
                Role: {value.role}
              </Chip>
            )}
            {value.company && (
              <Chip
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => onChange({ ...value, company: null })}
              >
                Company: {value.company}
              </Chip>
            )}
            {value.locations?.map((loc) => (
              <Chip
                key={loc.country}
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => removeLocationRequirement(loc.country)}
              >
                {loc.country}{loc.cities && loc.cities.length > 0 ? `: ${loc.cities.join(', ')}` : ': Any'}
              </Chip>
            ))}
            {value.years_experience && (
              <Chip
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => onChange({ ...value, years_experience: null })}
              >
                Experience: {value.years_experience}+ years
              </Chip>
            )}
            {value.education?.map((edu) => (
              <Chip
                key={edu.level}
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => removeEducationRequirement(edu.level)}
              >
                {edu.level}{edu.statuses && edu.statuses.length > 0 ? `: ${edu.statuses.join(', ')}` : ': Any'}
              </Chip>
            ))}
            {value.languages?.map((req) => (
              <Chip
                key={req.language}
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => removeLanguageRequirement(req.language)}
              >
                {req.language}: {req.min_cefr}+
              </Chip>
            ))}
            {value.skills?.map((skill) => (
              <Chip
                key={skill}
                style={{ fontSize: "var(--text-xs)" }}
                onRemove={() => toggleSkill(skill)}
              >
                {skill}
              </Chip>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}