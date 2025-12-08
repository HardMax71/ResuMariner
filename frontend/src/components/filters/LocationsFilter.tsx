import { useState } from 'react';
import type { LocationRequirement, CountryOption } from '../../api/client';
import Badge from '../Badge';
import Chip from '../Chip';
import { useClickOutside } from '../../hooks/useClickOutside';
import { PopupContainer, PopupTitle, CheckboxList, CheckboxLabel, FilterLabel } from './styled';

interface Props {
  locations: CountryOption[];
  selectedLocations: LocationRequirement[];
  onChange: (locations: LocationRequirement[]) => void;
}

function arraysEqual(a: string[] | null | undefined, b: string[]): boolean {
  if (!a || a.length === 0) return b.length === 0;
  if (a.length !== b.length) return false;
  const sortedA = [...a].sort();
  const sortedB = [...b].sort();
  return sortedA.every((val, idx) => val === sortedB[idx]);
}

export function LocationsFilter({ locations, selectedLocations, onChange }: Props) {
  const [expandedCountry, setExpandedCountry] = useState<string | null>(null);

  const ref = useClickOutside<HTMLDivElement>(() => setExpandedCountry(null), !!expandedCountry);

  const toggleCountry = (country: string, cities: string[]) => {
    const existing = selectedLocations.find(l => l.country === country);

    if (existing) {
      if (arraysEqual(existing.cities, cities)) {
        onChange(selectedLocations.filter(l => l.country !== country));
      } else {
        onChange(
          selectedLocations.map(l =>
            l.country === country ? { ...l, cities: cities.length === 0 ? null : cities } : l
          )
        );
      }
    } else {
      onChange([...selectedLocations, { country, cities: cities.length === 0 ? null : cities }]);
    }
    setExpandedCountry(null);
  };

  if (locations.length === 0) return null;

  return (
    <div className="mb-3" ref={ref}>
      <FilterLabel>
        Location
        {selectedLocations.length > 0 && (
          <Badge style={{ marginLeft: "var(--space-1)" }}>
            {selectedLocations.length}
          </Badge>
        )}
      </FilterLabel>
      <div className="chips">
        {locations.map((countryOption) => {
          const selected = selectedLocations.find(l => l.country === countryOption.country);
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

              {isExpanded && (
                <PopupContainer
                  style={{ minWidth: "min(15rem, 50vw)", width: "max-content", maxWidth: "min(20rem, 80vw)" }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <PopupTitle>Select cities in {countryOption.country}</PopupTitle>
                  <CheckboxList style={{ maxHeight: "50vh" }}>
                    <CheckboxLabel>
                      <input
                        type="checkbox"
                        checked={!selected?.cities || selected.cities.length === 0}
                        onChange={() => toggleCountry(countryOption.country, [])}
                      />
                      <span>Any City</span>
                    </CheckboxLabel>
                    {countryOption.cities.map(city => {
                      const currentCities = selected?.cities ?? [];
                      const isChecked = currentCities.includes(city);

                      return (
                        <CheckboxLabel key={city}>
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
                          <span>{city}</span>
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
