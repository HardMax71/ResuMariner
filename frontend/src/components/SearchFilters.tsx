import { useMemo } from "react";
import type { SearchFiltersSchema } from "../api/client";
import { useFilterOptions } from "../hooks/useResumeSearch";
import { SearchableDropdown } from "./filters/SearchableDropdown";
import { SkillsFilter } from "./filters/SkillsFilter";
import { LocationsFilter } from "./filters/LocationsFilter";
import { EducationFilter } from "./filters/EducationFilter";
import { LanguagesFilter } from "./filters/LanguagesFilter";
import { ActiveFiltersBar } from "./filters/ActiveFiltersBar";
import { FilterGrid, FilterInputWrapper, FilterLabel } from "./filters/styled";
import { getErrorMessage } from "../utils/error";

type Props = {
  value: SearchFiltersSchema;
  onChange: (v: SearchFiltersSchema) => void;
};

export default function SearchFiltersComp({ value, onChange }: Props) {
  const { data: opts, isLoading: loading, error: queryError } = useFilterOptions();
  const error = queryError ? getErrorMessage(queryError) : null;

  const companies = useMemo(() => opts?.companies ?? [], [opts]);
  const roles = useMemo(() => opts?.roles ?? [], [opts]);
  const countries = useMemo(() => opts?.countries ?? [], [opts]);
  const skills = useMemo(() => opts?.skills ?? [], [opts]);
  const educationLevels = useMemo(() => opts?.education_levels ?? [], [opts]);
  const languages = useMemo(() => opts?.languages ?? [], [opts]);

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

  return (
    <div className="filters-compact">
      {/* Dropdown Filters in Grid */}
      <FilterGrid>
        <SearchableDropdown
          label="Role"
          placeholder="Search role..."
          value={value.role ?? null}
          options={roles}
          onChange={(role) => onChange({ ...value, role })}
        />

        <SearchableDropdown
          label="Company"
          placeholder="Search company..."
          value={value.company ?? null}
          options={companies}
          onChange={(company) => onChange({ ...value, company })}
        />

        <FilterInputWrapper>
          <FilterLabel>Min Experience (years)</FilterLabel>
          <input
            type="number"
            min={0}
            placeholder="Min 0"
            value={value.years_experience ?? ""}
            onChange={(e) =>
              onChange({ ...value, years_experience: e.target.value ? Number(e.target.value) : null })
            }
            style={{
              MozAppearance: "textfield",
              WebkitAppearance: "none",
              appearance: "textfield",
            }}
            onWheel={(e) => e.currentTarget.blur()}
          />
        </FilterInputWrapper>
      </FilterGrid>

      {/* Location Filter */}
      <LocationsFilter
        locations={countries}
        selectedLocations={value.locations ?? []}
        onChange={(locations) => onChange({ ...value, locations })}
      />

      {/* Education Filter */}
      <EducationFilter
        educationLevels={educationLevels}
        selectedEducation={value.education ?? []}
        onChange={(education) => onChange({ ...value, education })}
      />

      {/* Languages Filter */}
      <LanguagesFilter
        languages={languages}
        selectedLanguages={value.languages ?? []}
        onChange={(languages) => onChange({ ...value, languages })}
      />

      {/* Skills Filter */}
      <SkillsFilter
        skills={skills}
        selectedSkills={value.skills ?? []}
        onChange={(skills) => onChange({ ...value, skills })}
      />

      {/* Active Filters Bar */}
      <ActiveFiltersBar
        filters={value}
        onRemoveRole={() => onChange({ ...value, role: null })}
        onRemoveCompany={() => onChange({ ...value, company: null })}
        onRemoveLocation={(country) => onChange({
          ...value,
          locations: value.locations?.filter(l => l.country !== country)
        })}
        onRemoveExperience={() => onChange({ ...value, years_experience: null })}
        onRemoveEducation={(level) => onChange({
          ...value,
          education: value.education?.filter(e => e.level !== level)
        })}
        onRemoveLanguage={(language) => onChange({
          ...value,
          languages: value.languages?.filter(l => l.language !== language)
        })}
        onRemoveSkill={(skill) => {
          const current = new Set(value.skills ?? []);
          current.delete(skill);
          onChange({ ...value, skills: Array.from(current) });
        }}
      />
    </div>
  );
}
