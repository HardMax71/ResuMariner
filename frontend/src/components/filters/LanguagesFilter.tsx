import { useState } from 'react';
import styled from '@emotion/styled';
import type { LanguageRequirement } from '../../api/client';
import Badge from '../Badge';
import Chip from '../Chip';
import { useClickOutside } from '../../hooks/useClickOutside';
import { FilterLabel } from './styled';

const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

const PopupContainer = styled.div`
  position: absolute;
  top: calc(100% + var(--space-1) / 2);
  left: 0;
  z-index: 10;
  background: white;
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-sm);
  padding: var(--space-1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  gap: calc(var(--space-1) / 2);
  min-width: 50%;
`;

const LevelButton = styled.button<{ selected?: boolean }>`
  flex: 1;
  padding: var(--space-1);
  font-size: var(--text-xs);
  border: 1px solid ${props => props.selected ? 'var(--primary-600)' : 'var(--neutral-300)'};
  background: ${props => props.selected ? 'var(--primary-50)' : 'white'};
  color: ${props => props.selected ? 'var(--primary-700)' : 'var(--neutral-700)'};
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: ${props => props.selected ? 600 : 400};
  transition: all var(--transition-fast);

  &:hover {
    background: ${props => props.selected ? 'var(--primary-100)' : 'var(--neutral-50)'};
    border-color: ${props => props.selected ? 'var(--primary-700)' : 'var(--neutral-400)'};
  }
`;

interface LanguageOption {
  language: string;
  resume_count: number;
}

interface Props {
  languages: LanguageOption[];
  selectedLanguages: LanguageRequirement[];
  onChange: (languages: LanguageRequirement[]) => void;
}

export function LanguagesFilter({ languages, selectedLanguages, onChange }: Props) {
  const [expandedLanguage, setExpandedLanguage] = useState<string | null>(null);

  const ref = useClickOutside<HTMLDivElement>(() => setExpandedLanguage(null), !!expandedLanguage);

  const toggleLanguage = (language: string, level: string) => {
    const existing = selectedLanguages.find(l => l.language === language);

    if (existing) {
      if (existing.min_cefr === level) {
        onChange(selectedLanguages.filter(l => l.language !== language));
      } else {
        onChange(
          selectedLanguages.map(l =>
            l.language === language ? { ...l, min_cefr: level } : l
          )
        );
      }
    } else {
      onChange([...selectedLanguages, { language, min_cefr: level }]);
    }
    setExpandedLanguage(null);
  };

  if (languages.length === 0) return null;

  return (
    <div className="mb-3" ref={ref}>
      <FilterLabel className="label small">
        Languages
        {selectedLanguages.length > 0 && (
          <Badge style={{ marginLeft: "var(--space-1)" }}>
            {selectedLanguages.length}
          </Badge>
        )}
      </FilterLabel>
      <div className="chips">
        {languages.map((langOption) => {
          const selected = selectedLanguages.find(l => l.language === langOption.language);
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
                <span style={{ opacity: 0.6, marginLeft: "calc(var(--space-1) / 2)" }}>
                  {langOption.resume_count}
                </span>
              </Chip>

              {isExpanded && (
                <PopupContainer onClick={(e) => e.stopPropagation()}>
                  {CEFR_LEVELS.map(level => (
                    <LevelButton
                      key={level}
                      type="button"
                      selected={selected?.min_cefr === level}
                      onClick={() => toggleLanguage(langOption.language, level)}
                    >
                      {level}
                    </LevelButton>
                  ))}
                </PopupContainer>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
