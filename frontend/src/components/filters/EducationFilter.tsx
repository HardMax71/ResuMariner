import { useState } from 'react';
import type { EducationRequirement, StatusesEnum } from '../../api/client';
import Badge from '../Badge';
import Chip from '../Chip';
import { useClickOutside } from '../../hooks/useClickOutside';
import { PopupContainer, PopupTitle, CheckboxList, CheckboxLabel, FilterLabel } from './styled';

interface EducationOption {
  level: string;
  statuses: string[];
  resume_count: number;
}

interface Props {
  educationLevels: EducationOption[];
  selectedEducation: EducationRequirement[];
  onChange: (education: EducationRequirement[]) => void;
}

export function EducationFilter({ educationLevels, selectedEducation, onChange }: Props) {
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null);

  const ref = useClickOutside<HTMLDivElement>(() => setExpandedLevel(null), !!expandedLevel);

  const toggleEducationLevel = (level: string, statuses: string[]) => {
    const existing = selectedEducation.find(e => e.level === level);
    const typedStatuses = statuses as StatusesEnum[];

    if (existing) {
      const sameStatusesSelected = JSON.stringify(existing.statuses?.sort()) === JSON.stringify(statuses.sort());
      if (sameStatusesSelected) {
        onChange(selectedEducation.filter(e => e.level !== level));
      } else {
        onChange(
          selectedEducation.map(e =>
            e.level === level ? { ...e, statuses: typedStatuses.length === 0 ? null : typedStatuses } : e
          )
        );
      }
    } else {
      onChange([...selectedEducation, { level, statuses: typedStatuses.length === 0 ? null : typedStatuses }]);
    }
    setExpandedLevel(null);
  };

  if (educationLevels.length === 0) return null;

  return (
    <div className="mb-3" ref={ref}>
      <FilterLabel className="label small">
        Education
        {selectedEducation.length > 0 && (
          <Badge style={{ marginLeft: "var(--space-1)" }}>
            {selectedEducation.length}
          </Badge>
        )}
      </FilterLabel>
      <div className="chips">
        {educationLevels.map((levelOption) => {
          const selected = selectedEducation.find(e => e.level === levelOption.level);
          const isExpanded = expandedLevel === levelOption.level;

          return (
            <div key={levelOption.level} style={{ position: "relative", display: "inline-block" }}>
              <Chip
                selectable
                selected={!!selected}
                onClick={(e) => {
                  e.stopPropagation();
                  setExpandedLevel(isExpanded ? null : levelOption.level);
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

              {isExpanded && (
                <PopupContainer onClick={(e) => e.stopPropagation()}>
                  <PopupTitle>Select status for {levelOption.level}</PopupTitle>
                  <CheckboxList>
                    <CheckboxLabel>
                      <input
                        type="checkbox"
                        checked={!selected?.statuses || selected.statuses.length === 0}
                        onChange={() => toggleEducationLevel(levelOption.level, [])}
                      />
                      <span>Any Status</span>
                    </CheckboxLabel>
                    {levelOption.statuses.map(status => {
                      const currentStatuses = selected?.statuses ?? [];
                      const isChecked = currentStatuses.includes(status as StatusesEnum);

                      return (
                        <CheckboxLabel key={status}>
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
                          <span>{status}</span>
                        </CheckboxLabel>
                      );
                    })}
                  </CheckboxList>
                </PopupContainer>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
