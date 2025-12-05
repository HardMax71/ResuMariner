import { ReactNode, useState } from "react";
import styled from "@emotion/styled";

const TooltipWrapper = styled.div`
  position: relative;
  display: inline-flex;
  align-items: center;
`;

const TooltipContent = styled.div<{ visible: boolean }>`
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius-lg);
  white-space: nowrap;
  pointer-events: none;
  opacity: ${props => props.visible ? 1 : 0};
  visibility: ${props => props.visible ? "visible" : "hidden"};
  transition: opacity 0.2s, visibility 0.2s;
  z-index: 1000;

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: rgba(0, 0, 0, 0.9);
  }
`;

interface TooltipProps {
  text: string;
  children: ReactNode;
}

export default function Tooltip({ text, children }: TooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <TooltipWrapper
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      <TooltipContent visible={visible}>
        {text}
      </TooltipContent>
    </TooltipWrapper>
  );
}
