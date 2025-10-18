import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SelectedCandidate {
  uid: string;
  name: string;
}

interface SelectionContextType {
  selected: SelectedCandidate[];
  toggleSelection: (uid: string, name: string) => void;
  clearSelection: () => void;
  isSelected: (uid: string) => boolean;
  getSelectedUids: () => string[];
}

const SelectionContext = createContext<SelectionContextType | undefined>(undefined);

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selected, setSelected] = useState<SelectedCandidate[]>(() => {
    const saved = localStorage.getItem('selectedCandidates');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('selectedCandidates', JSON.stringify(selected));
  }, [selected]);

  const toggleSelection = (uid: string, name: string) => {
    setSelected(prev => {
      const exists = prev.find(c => c.uid === uid);
      if (exists) {
        return prev.filter(c => c.uid !== uid);
      } else {
        if (prev.length >= 5) {
          return prev;
        }
        return [...prev, { uid, name }];
      }
    });
  };

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
    <SelectionContext.Provider value={{ selected, toggleSelection, clearSelection, isSelected, getSelectedUids }}>
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
