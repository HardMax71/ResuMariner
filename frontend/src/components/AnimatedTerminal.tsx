import { useEffect, useState, useRef, useCallback } from 'react';

// Animation timing constants (in milliseconds)
const TIMING = {
  TYPING_SPEED: 50,
  AFTER_COMMAND_DELAY: 500,
  PROCESSING_DELAY: 1500,
  BEFORE_SECOND_COMMAND: 1000,
  AFTER_RESULT_DELAY: 500,
} as const;

// Layout constants for command width calculation
const LAYOUT = {
  CHAR_WIDTH_PX: 8,
  PADDING_PX: 20,
  PROMPT_CHARS: 2,
} as const;

// Terminal command strings
const COMMANDS = {
  SINGLE_LINE: 'curl -X POST /api/v1/resumes -F "file=@resume.pdf"',
  MULTI_LINE: 'curl -X POST /api/v1/resumes \\\n  -F "file=@resume.pdf"',
  RESULT: 'curl /api/v1/resumes/abc-123/',
} as const;

interface AnimatedTerminalProps {
  isVisible: boolean;
}

export default function AnimatedTerminal({ isVisible }: AnimatedTerminalProps) {
  const [terminalStep, setTerminalStep] = useState(0);
  const [typedCommand, setTypedCommand] = useState('');
  const [typedResultCommand, setTypedResultCommand] = useState('');
  const [commandText, setCommandText] = useState('');
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // Measure and decide which command format to use
  useEffect(() => {
    if (!contentRef.current) return;

    const checkWidth = () => {
      const containerWidth = contentRef.current?.clientWidth || 0;
      const commandLength = COMMANDS.SINGLE_LINE.length + LAYOUT.PROMPT_CHARS;
      const estimatedWidth = commandLength * LAYOUT.CHAR_WIDTH_PX;

      if (estimatedWidth + LAYOUT.PADDING_PX < containerWidth) {
        setCommandText(COMMANDS.SINGLE_LINE);
      } else {
        setCommandText(COMMANDS.MULTI_LINE);
      }
    };

    checkWidth();

    const resizeObserver = new ResizeObserver(checkWidth);
    resizeObserver.observe(contentRef.current);

    return () => resizeObserver.disconnect();
  }, []);

  // Terminal typing animation
  useEffect(() => {
    if (!isVisible || !commandText) return;

    if (prefersReducedMotion) {
      setTypedCommand(commandText);
      setTerminalStep(4);
      setTypedResultCommand(COMMANDS.RESULT);
      return;
    }

    setTerminalStep(0);
    setTypedCommand('');
    setTypedResultCommand('');

    let charIndex = 0;
    const typeInterval = setInterval(() => {
      if (charIndex < commandText.length) {
        setTypedCommand(commandText.slice(0, charIndex + 1));
        charIndex++;
      } else {
        clearInterval(typeInterval);
        setTimeout(() => setTerminalStep(1), TIMING.AFTER_COMMAND_DELAY);
      }
    }, TIMING.TYPING_SPEED);

    return () => clearInterval(typeInterval);
  }, [isVisible, commandText, prefersReducedMotion]);

  // Handle subsequent animation steps
  useEffect(() => {
    if (prefersReducedMotion) return;

    if (terminalStep === 1) {
      const timer = setTimeout(() => setTerminalStep(2), TIMING.PROCESSING_DELAY);
      return () => clearTimeout(timer);
    } else if (terminalStep === 2) {
      const timer = setTimeout(() => {
        setTerminalStep(3);
        setTypedResultCommand('');
      }, TIMING.BEFORE_SECOND_COMMAND);
      return () => clearTimeout(timer);
    } else if (terminalStep === 3) {
      let charIndex = 0;
      const typeInterval = setInterval(() => {
        if (charIndex < COMMANDS.RESULT.length) {
          setTypedResultCommand(COMMANDS.RESULT.slice(0, charIndex + 1));
          charIndex++;
        } else {
          clearInterval(typeInterval);
          setTimeout(() => setTerminalStep(4), TIMING.AFTER_RESULT_DELAY);
        }
      }, TIMING.TYPING_SPEED);
      return () => clearInterval(typeInterval);
    }
  }, [terminalStep, prefersReducedMotion]);

  // Helper for visibility classes
  const vis = useCallback((step: number) =>
    terminalStep >= step ? 'terminal-visible' : 'terminal-hidden'
  , [terminalStep]);

  const JsonLine = useCallback(({ keyName, value, comma = true }: { keyName: string; value: string; comma?: boolean }) => (
    <div className="landing-terminal-line landing-terminal-line-indent">
      <span className="landing-terminal-json-key">"{keyName}"</span>
      <span className="landing-terminal-json-punct">: </span>
      <span className="landing-terminal-json-value">"{value}"</span>
      {comma && <span className="landing-terminal-json-punct">,</span>}
    </div>
  ), []);

  return (
    <div className="landing-terminal" role="img" aria-label="Terminal demo showing API interaction">
      {/* Terminal Header */}
      <div className="landing-terminal-header">
        <div className="landing-terminal-dots" aria-hidden="true">
          <div className="landing-terminal-dot landing-terminal-dot-red" />
          <div className="landing-terminal-dot landing-terminal-dot-yellow" />
          <div className="landing-terminal-dot landing-terminal-dot-green" />
        </div>
        <span className="landing-terminal-title">resumariner.sh</span>
      </div>

      {/* Terminal Content - ALL content pre-rendered, visibility controlled */}
      <div ref={contentRef} className="landing-terminal-content">
        {/* Command block - contains 1 or 2 lines */}
        <div className="landing-terminal-cmd-block">
          <div className="landing-terminal-line">
            <span className="landing-terminal-prompt">$</span>
            <span className="landing-terminal-command">
              {' '}
              {typedCommand.split('\n')[0] || commandText.split('\n')[0]}
              {typedCommand.split('\n')[0] && !typedCommand.includes('\n') && typedCommand.length < commandText.length && !prefersReducedMotion && (
                <span className="landing-terminal-cursor" />
              )}
            </span>
          </div>
          {/* Second line of command - only if multi-line */}
          {commandText.includes('\n') && (
            <div className="landing-terminal-line landing-terminal-line-indent">
              <span className="landing-terminal-command">
                {typedCommand.includes('\n') ? typedCommand.split('\n')[1] : commandText.split('\n')[1] || ''}
                {typedCommand.includes('\n') && typedCommand.split('\n')[1]?.length < (commandText.split('\n')[1]?.length || 0) && !prefersReducedMotion && (
                  <span className="landing-terminal-cursor" />
                )}
              </span>
            </div>
          )}
        </div>

        {/* Processing text - always in DOM */}
        <div className={`landing-terminal-line landing-terminal-processing ${vis(1)}`}>
          Processing...
        </div>

        {/* First response block - always in DOM (5 lines) */}
        <div className={`landing-terminal-response landing-terminal-response-5 ${vis(2)}`}>
          <div className="landing-terminal-line">
            <span className="landing-terminal-json-punct">{'{'}</span>
          </div>
          <JsonLine keyName="uid" value="abc-123" />
          <JsonLine keyName="status" value="completed" />
          <JsonLine keyName="processing_time" value="28s" comma={false} />
          <div className="landing-terminal-line">
            <span className="landing-terminal-json-punct">{'}'}</span>
          </div>
        </div>

        {/* Second command - always in DOM */}
        <div className={`landing-terminal-line ${vis(3)}`}>
          <span className="landing-terminal-prompt">$</span>
          <span className="landing-terminal-command">
            {' '}
            {terminalStep >= 3 ? typedResultCommand : COMMANDS.RESULT}
            {terminalStep === 3 && typedResultCommand.length < COMMANDS.RESULT.length && !prefersReducedMotion && (
              <span className="landing-terminal-cursor" />
            )}
          </span>
        </div>

        {/* Second response block - always in DOM (8 lines) */}
        <div className={`landing-terminal-response landing-terminal-response-8 ${vis(4)}`}>
          <div className="landing-terminal-line">
            <span className="landing-terminal-json-punct">{'{'}</span>
          </div>
          <JsonLine keyName="name" value="John Doe" />
          <JsonLine keyName="email" value="john@example.com" />
          <div className="landing-terminal-line landing-terminal-line-indent">
            <span className="landing-terminal-json-key">"skills"</span>
            <span className="landing-terminal-json-punct">: [</span>
            <span className="landing-terminal-json-value">"Python", "Django", "React"</span>
            <span className="landing-terminal-json-punct">],</span>
          </div>
          <JsonLine keyName="experience" value="5 years" />
          <JsonLine keyName="role" value="Senior Engineer" />
          <JsonLine keyName="ai_review" value="Strong technical profile. Consider adding metrics." comma={false} />
          <div className="landing-terminal-line">
            <span className="landing-terminal-json-punct">{'}'}</span>
          </div>
        </div>

        {/* Final cursor - always in DOM */}
        <div className={`landing-terminal-line landing-terminal-line-flex ${vis(4)}`}>
          <span className="landing-terminal-prompt">$</span>
          {!prefersReducedMotion && (
            <span className="landing-terminal-cursor" />
          )}
        </div>
      </div>
    </div>
  );
}
