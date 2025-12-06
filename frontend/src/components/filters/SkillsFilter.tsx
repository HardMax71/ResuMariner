import { useState, useMemo } from 'react';
import Badge from '../Badge';
import Chip from '../Chip';
import { FilterLabel } from './styled';

interface Skill {
  value: string;
  count: number;
}

interface Props {
  skills: Skill[];
  selectedSkills: string[];
  onChange: (skills: string[]) => void;
}

export function SkillsFilter({ skills, selectedSkills, onChange }: Props) {
  const [showAll, setShowAll] = useState(false);

  const visibleSkills = useMemo(() => {
    return showAll ? skills : skills.slice(0, 12);
  }, [skills, showAll]);

  const toggleSkill = (skillValue: string) => {
    const current = new Set(selectedSkills);
    if (current.has(skillValue)) {
      current.delete(skillValue);
    } else {
      current.add(skillValue);
    }
    onChange(Array.from(current));
  };

  if (skills.length === 0) return null;

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-2">
        <FilterLabel>
          Skills
          {selectedSkills.length > 0 && (
            <Badge style={{ marginLeft: "var(--space-1)" }}>
              {selectedSkills.length}
            </Badge>
          )}
        </FilterLabel>

        {skills.length > 12 && (
          <button
            type="button"
            className="text-sm"
            onClick={() => setShowAll(!showAll)}
            style={{
              background: "none",
              border: "none",
              color: "var(--primary-600)",
              cursor: "pointer",
              padding: 0,
              fontSize: "var(--text-sm)",
            }}
          >
            {showAll ? "Show Less" : `Show All (${skills.length})`}
          </button>
        )}
      </div>

      <div
        className="chips"
        style={{
          maxHeight: showAll ? "none" : "72px",
          overflow: "hidden"
        }}
      >
        {visibleSkills.map((skill) => {
          const selected = selectedSkills.includes(skill.value);
          return (
            <Chip
              key={skill.value}
              selectable
              selected={selected}
              onClick={() => toggleSkill(skill.value)}
              title={`${skill.value} (${skill.count})`}
              style={{ fontSize: "var(--text-xs)" }}
            >
              {skill.value}
              <span style={{ opacity: 0.6, marginLeft: "4px" }}>
                {skill.count}
              </span>
            </Chip>
          );
        })}
      </div>
    </div>
  );
}
