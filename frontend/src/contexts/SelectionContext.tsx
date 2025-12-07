import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SelectedCandidate {
  uid: string;
  name: string;
}

interface SelectionContextType {
  selected: SelectedCandidate[];
  toggleSelection: (uid: string, name: string) => boolean;
  clearSelection: () => void;
  isSelected: (uid: string) => boolean;
  getSelectedUids: () => string[];
  maxReached: boolean;
}

const SelectionContext = createContext<SelectionContextType | undefined>(undefined);

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selected, setSelected] = useState<SelectedCandidate[]>(() => {
    try {
      const saved = localStorage.getItem('selectedCandidates');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('selectedCandidates', JSON.stringify(selected));
  }, [selected]);

  const toggleSelection = (uid: string, name: string): boolean => {
    const exists = selected.find(c => c.uid === uid);
    if (exists) {
      setSelected(prev => prev.filter(c => c.uid !== uid));
      return true;
    }
    if (selected.length >= 5) {
      return false;
    }
    setSelected(prev => [...prev, { uid, name }]);
    return true;
  };

  const maxReached = selected.length >= 5;

  const clearSelection = () => {
    setSelected([]);
    localStorage.removeItem('selectedCandidates');
  };

  const isSelected = (uid: string) => {
    return selected.some(c => c.uid === uid);
  };

  const getSelectedUids = () => {
    return selected.map(c => c.uid);
  };

  return (
    <SelectionContext.Provider value={{ selected, toggleSelection, clearSelection, isSelected, getSelectedUids, maxReached }}>
      {children}
    </SelectionContext.Provider>
  );
}

export function useSelection() {
  const context = useContext(SelectionContext);
  if (!context) {
    throw new Error('useSelection must be used within SelectionProvider');
  }
  return context;
}
