import { useState, useMemo, useEffect } from 'react';
import { useClickOutside } from '../../hooks/useClickOutside';
import {
  DropdownContainer,
  DropdownItem,
  DropdownCount,
  DropdownEmpty,
  FilterInputWrapper,
  FilterLabel
} from './styled';

interface Option {
  value: string;
  count: number;
}

interface Props {
  label: string;
  placeholder?: string;
  value: string | null;
  options: Option[];
  onChange: (value: string | null) => void;
}

export function SearchableDropdown({ label, placeholder, value, options, onChange }: Props) {
  const [searchTerm, setSearchTerm] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const ref = useClickOutside<HTMLDivElement>(() => setIsOpen(false), isOpen);

  const filteredOptions = useMemo(() => {
    if (!searchTerm.trim()) return options;
    const search = searchTerm.toLowerCase();
    return options.filter(opt => opt.value.toLowerCase().includes(search));
  }, [options, searchTerm]);

  // Sync search term when value changes externally (e.g., Clear All)
  useEffect(() => {
    if (!value) setSearchTerm("");
  }, [value]);

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setSearchTerm(optionValue);
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setSearchTerm("");
    setIsOpen(false);
  };

  return (
    <FilterInputWrapper ref={ref}>
      <FilterLabel>{label}</FilterLabel>
      <input
        type="text"
        placeholder={placeholder || `Search ${label.toLowerCase()}...`}
        value={value || searchTerm}
        onChange={(e) => {
          setSearchTerm(e.target.value);
          if (!e.target.value) onChange(null);
        }}
        onFocus={() => setIsOpen(true)}
        onClick={(e) => e.stopPropagation()}
      />

      {isOpen && (
        <DropdownContainer onClick={(e) => e.stopPropagation()}>
          <DropdownItem isClear onClick={handleClear}>
            Any {label}
          </DropdownItem>

          {filteredOptions.map((opt) => (
            <DropdownItem
              key={opt.value}
              selected={value === opt.value}
              onClick={() => handleSelect(opt.value)}
            >
              <span>{opt.value}</span>
              <DropdownCount>{opt.count}</DropdownCount>
            </DropdownItem>
          ))}

          {filteredOptions.length === 0 && (
            <DropdownEmpty>No matching {label.toLowerCase()}</DropdownEmpty>
          )}
        </DropdownContainer>
      )}
    </FilterInputWrapper>
  );
}
