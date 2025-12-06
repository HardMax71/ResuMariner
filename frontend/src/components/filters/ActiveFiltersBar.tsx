import type { SearchFiltersSchema } from '../../api/client';
import Chip from '../Chip';

interface Props {
  filters: SearchFiltersSchema;
  onRemoveRole: () => void;
  onRemoveCompany: () => void;
  onRemoveLocation: (country: string) => void;
  onRemoveExperience: () => void;
  onRemoveEducation: (level: string) => void;
  onRemoveLanguage: (language: string) => void;
  onRemoveSkill: (skill: string) => void;
}

export function ActiveFiltersBar({
  filters,
  onRemoveRole,
  onRemoveCompany,
  onRemoveLocation,
  onRemoveExperience,
  onRemoveEducation,
  onRemoveLanguage,
  onRemoveSkill
}: Props) {
  const hasFilters =
    filters.skills?.length ||
    filters.role ||
    filters.company ||
    filters.locations?.length ||
    filters.years_experience ||
    filters.education?.length ||
    filters.languages?.length;

  if (!hasFilters) return null;

  return (
    <div
      className="flex items-center gap-2"
      style={{
        marginTop: "var(--space-2)",
        padding: "var(--space-1) 0"
      }}
    >
      <span className="small muted">Active filters:</span>
      <div className="chips">
        {filters.role && (
          <Chip
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={onRemoveRole}
          >
            Role: {filters.role}
          </Chip>
        )}

        {filters.company && (
          <Chip
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={onRemoveCompany}
          >
            Company: {filters.company}
          </Chip>
        )}

        {filters.locations?.map((loc) => (
          <Chip
            key={loc.country}
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={() => onRemoveLocation(loc.country)}
          >
            {loc.country}{loc.cities && loc.cities.length > 0 ? `: ${loc.cities.join(', ')}` : ': Any'}
          </Chip>
        ))}

        {filters.years_experience && (
          <Chip
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={onRemoveExperience}
          >
            Experience: {filters.years_experience}+ years
          </Chip>
        )}

        {filters.education?.map((edu) => (
          <Chip
            key={edu.level}
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={() => onRemoveEducation(edu.level)}
          >
            {edu.level}{edu.statuses && edu.statuses.length > 0 ? `: ${edu.statuses.join(', ')}` : ': Any'}
          </Chip>
        ))}

        {filters.languages?.map((req) => (
          <Chip
            key={req.language}
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={() => onRemoveLanguage(req.language)}
          >
            {req.language}: {req.min_cefr}+
          </Chip>
        ))}

        {filters.skills?.map((skill) => (
          <Chip
            key={skill}
            style={{ fontSize: "var(--text-xs)" }}
            onRemove={() => onRemoveSkill(skill)}
          >
            {skill}
          </Chip>
        ))}
      </div>
    </div>
  );
}
