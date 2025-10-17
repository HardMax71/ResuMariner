import styled from '@emotion/styled';

export const DropdownContainer = styled.div`
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 20;
  background: var(--neutral-0);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-sm);
  max-height: 250px;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
`;

export const DropdownItem = styled.div<{ selected?: boolean; isClear?: boolean }>`
  padding: var(--space-1) var(--space-2);
  cursor: pointer;
  font-size: var(--text-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: ${props => props.selected ? 'var(--primary-50)' : 'var(--neutral-0)'};
  color: ${props => props.selected ? 'var(--primary-700)' : props.isClear ? 'var(--neutral-600)' : 'var(--neutral-700)'};
  font-weight: ${props => props.selected ? 600 : props.isClear ? 500 : 400};
  border-bottom: ${props => props.isClear ? '1px solid var(--neutral-200)' : 'none'};
  transition: background var(--transition-fast);

  &:hover {
    background: ${props => props.selected ? 'var(--primary-50)' : 'var(--neutral-50)'};
  }
`;

export const DropdownCount = styled.span`
  color: var(--neutral-500);
  font-size: var(--text-xs);
  font-weight: 500;
`;

export const DropdownEmpty = styled.div`
  padding: var(--space-2);
  text-align: center;
  color: var(--neutral-500);
  font-size: var(--text-sm);
`;

export const PopupContainer = styled.div`
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 10;
  background: white;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-sm);
  padding: var(--space-2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
`;

export const PopupTitle = styled.div`
  margin-bottom: var(--space-1);
  font-weight: 600;
  font-size: var(--text-sm);
`;

export const CheckboxList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 200px;
  overflow-y: auto;
`;

export const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px;
  font-size: var(--text-sm);
  transition: background var(--transition-fast);

  &:hover {
    background: var(--neutral-50);
    border-radius: var(--radius-sm);
  }
`;

export const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-2);
  margin-bottom: var(--space-3);
`;

export const FilterInputWrapper = styled.div`
  position: relative;
`;

export const FilterLabel = styled.label`
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-700);
  margin-bottom: 4px;
`;
