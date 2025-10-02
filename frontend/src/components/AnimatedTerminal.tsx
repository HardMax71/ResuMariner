import { useEffect, useState, useRef } from 'react';

interface AnimatedTerminalProps {
  isVisible: boolean;
}

export default function AnimatedTerminal({ isVisible }: AnimatedTerminalProps) {
  const [terminalStep, setTerminalStep] = useState(0);
  const [typedCommand, setTypedCommand] = useState('');
  const [typedResultCommand, setTypedResultCommand] = useState('');
  const [commandText, setCommandText] = useState('curl -X POST /api/v1/upload -F "file=@resume.pdf"');
  const typingSpeed = 50;
  const contentRef = useRef<HTMLDivElement>(null);

  const singleLineCommand = 'curl -X POST /api/v1/upload -F "file=@resume.pdf"';
  const multiLineCommand = 'curl -X POST /api/v1/upload \\\n  -F "file=@resume.pdf"';
  const resultCommand = 'curl /api/v1/jobs/abc-123/result/';

  // Measure and decide which command format to use
  useEffect(() => {
    if (!contentRef.current) return;

    const checkWidth = () => {
      const containerWidth = contentRef.current?.clientWidth || 0;
      // Create temporary span to measure text width
      const tempSpan = document.createElement('span');
      tempSpan.style.fontFamily = "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace";
      tempSpan.style.fontSize = '14px';
      tempSpan.style.visibility = 'hidden';
      tempSpan.style.position = 'absolute';
      tempSpan.style.whiteSpace = 'nowrap';
      tempSpan.textContent = '$ ' + singleLineCommand;
      document.body.appendChild(tempSpan);

      const textWidth = tempSpan.offsetWidth;
      document.body.removeChild(tempSpan);

      // If text fits with some margin (20px), use single line
      if (textWidth + 20 < containerWidth) {
        setCommandText(singleLineCommand);
      } else {
        setCommandText(multiLineCommand);
      }
    };

    checkWidth();
    window.addEventListener('resize', checkWidth);
    return () => window.removeEventListener('resize', checkWidth);
  }, []);

  // Terminal typing animation
  useEffect(() => {
    if (!isVisible) return;

    // Reset animation when terminal becomes visible
    setTerminalStep(0);
    setTypedCommand('');

    // Step 0: Type command character by character
    let charIndex = 0;
    const typeInterval = setInterval(() => {
      if (charIndex < commandText.length) {
        setTypedCommand(commandText.slice(0, charIndex + 1));
        charIndex++;
      } else {
        clearInterval(typeInterval);
        // Move to step 1 (processing) after command is typed
        setTimeout(() => setTerminalStep(1), 500);
      }
    }, typingSpeed);

    return () => clearInterval(typeInterval);
  }, [isVisible]);

  // Handle subsequent animation steps
  useEffect(() => {
    if (terminalStep === 1) {
      // Step 1: Show processing for 1.5s, then move to step 2 (result)
      const timer = setTimeout(() => setTerminalStep(2), 1500);
      return () => clearTimeout(timer);
    } else if (terminalStep === 2) {
      // Step 2: Show upload result for 1s, then move to step 3 (type result command)
      const timer = setTimeout(() => {
        setTerminalStep(3);
        setTypedResultCommand('');
      }, 1000);
      return () => clearTimeout(timer);
    } else if (terminalStep === 3) {
      // Step 3: Type result command
      let charIndex = 0;
      const typeInterval = setInterval(() => {
        if (charIndex < resultCommand.length) {
          setTypedResultCommand(resultCommand.slice(0, charIndex + 1));
          charIndex++;
        } else {
          clearInterval(typeInterval);
          // Move to step 4 (show result data) after command is typed
          setTimeout(() => setTerminalStep(4), 500);
        }
      }, typingSpeed);
      return () => clearInterval(typeInterval);
    }
  }, [terminalStep]);

  return (
    <div style={{
      background: 'var(--neutral-900)',
      border: '1.5px solid var(--neutral-700)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Terminal Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '12px 16px',
        background: 'var(--neutral-800)',
        borderBottom: '1px solid var(--neutral-700)'
      }}>
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ff5f56' }} />
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ffbd2e' }} />
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#27c93f' }} />
        <span style={{
          marginLeft: 'auto',
          fontSize: 'var(--text-xs)',
          color: 'var(--neutral-500)',
          fontFamily: 'var(--font-mono)'
        }}>
          resumariner.sh
        </span>
      </div>

      {/* Terminal Content */}
      <div
        ref={contentRef}
        style={{
          flex: 1,
          padding: 'var(--space-4)',
          fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace",
          fontSize: '14px',
          lineHeight: '1.6',
          color: 'var(--neutral-300)',
          overflowY: 'auto'
        }}
      >
        {/* Command line with typing animation */}
        <div style={{ marginBottom: 'clamp(8px, 1vw, 16px)' }}>
          <span style={{ color: 'var(--accent1-400)' }}>$</span>
          <span style={{ color: 'var(--neutral-0)' }}>
            {' '}
            {typedCommand.split('\n')[0]}
            {/* Show cursor only if we're still typing the first line AND command isn't complete */}
            {typedCommand.split('\n')[0] && !typedCommand.includes('\n') && typedCommand.length < commandText.length && (
              <span style={{
                display: 'inline-block',
                width: '9px',
                height: '18px',
                background: 'var(--neutral-0)',
                marginLeft: '2px',
                animation: 'cursor-blink 0.8s infinite',
                verticalAlign: 'middle'
              }} />
            )}
          </span>
        </div>
        {typedCommand.includes('\n') && (
          <div style={{ marginBottom: 'clamp(8px, 1vw, 16px)', paddingLeft: '16px' }}>
            <span style={{ color: 'var(--neutral-0)' }}>
              {typedCommand.split('\n')[1] || ''}
              {/* Show cursor only if we're still typing the second line */}
              {typedCommand.split('\n')[1] && typedCommand.split('\n')[1].length < commandText.split('\n')[1].length && (
                <span style={{
                  display: 'inline-block',
                  width: '9px',
                  height: '18px',
                  background: 'var(--neutral-0)',
                  marginLeft: '2px',
                  animation: 'cursor-blink 0.8s infinite',
                  verticalAlign: 'middle'
                }} />
              )}
            </span>
          </div>
        )}

        {/* Processing text - shows after command is fully typed */}
        {terminalStep >= 1 && (
          <div style={{
            marginBottom: 'clamp(8px, 1vw, 16px)',
            color: 'var(--neutral-500)',
            fontSize: '14px',
            lineHeight: '1.6',
            opacity: terminalStep >= 1 ? 1 : 0,
            transition: 'opacity 0.3s'
          }}>
            Processing...
          </div>
        )}

        {/* Response visualization - shows after processing */}
        {terminalStep >= 2 && (
          <div style={{
            background: 'rgba(67, 56, 202, 0.1)',
            border: '1px solid var(--primary-700)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px',
            marginBottom: 'clamp(8px, 1vw, 16px)',
            opacity: terminalStep >= 2 ? 1 : 0,
            transform: terminalStep >= 2 ? 'translateY(0)' : 'translateY(10px)',
            transition: 'opacity 0.4s, transform 0.4s'
          }}>
            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <span style={{ color: 'var(--neutral-500)' }}>{'{'}</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"job_id"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"abc-123"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"status"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"completed"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"processing_time"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"28s"</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <span style={{ color: 'var(--neutral-500)' }}>{'}'}</span>
            </div>
          </div>
        )}

        {/* Result command - step 3 */}
        {terminalStep >= 3 && (
          <div style={{ marginBottom: 'clamp(8px, 1vw, 16px)' }}>
            <div style={{ display: 'flex', alignItems: 'center', height: '22px' }}>
              <span style={{ color: 'var(--accent1-400)', fontSize: '14px', lineHeight: '1.6' }}>$</span>
              <span style={{ color: 'var(--neutral-0)', marginLeft: '6px' }}>
                {typedResultCommand}
                {terminalStep === 3 && typedResultCommand.length < resultCommand.length && (
                  <span style={{
                    display: 'inline-block',
                    width: '9px',
                    height: '18px',
                    background: 'var(--neutral-0)',
                    marginLeft: '2px',
                    animation: 'cursor-blink 0.8s infinite',
                    verticalAlign: 'middle'
                  }} />
                )}
              </span>
            </div>
          </div>
        )}

        {/* Result data - step 4 */}
        {terminalStep >= 4 && (
          <div style={{
            background: 'rgba(67, 56, 202, 0.1)',
            border: '1px solid var(--primary-700)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px',
            opacity: terminalStep >= 4 ? 1 : 0,
            transform: terminalStep >= 4 ? 'translateY(0)' : 'translateY(10px)',
            transition: 'opacity 0.4s, transform 0.4s',
            marginBottom: 'clamp(8px, 1vw, 16px)'
          }}>
            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <span style={{ color: 'var(--neutral-500)' }}>{'{'}</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"name"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"John Doe"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"email"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"john@example.com"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"skills"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: [</span>
              <span style={{ color: 'var(--accent1-400)' }}>"Python", "Django", "React"</span>
              <span style={{ color: 'var(--neutral-500)' }}>],</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"experience"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"5 years"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"role"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"Senior Engineer"</span>
              <span style={{ color: 'var(--neutral-500)' }}>,</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6', paddingLeft: '16px' }}>
              <span style={{ color: 'var(--primary-400)' }}>"ai_review"</span>
              <span style={{ color: 'var(--neutral-500)' }}>: </span>
              <span style={{ color: 'var(--accent1-400)' }}>"Strong technical profile. Consider adding metrics."</span>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <span style={{ color: 'var(--neutral-500)' }}>{'}'}</span>
            </div>
          </div>
        )}

        {/* Final cursor - shows after result data */}
        {terminalStep >= 4 && (
          <div style={{ display: 'flex', alignItems: 'center', height: '22px' }}>
            <span style={{ color: 'var(--accent1-400)', fontSize: '14px', lineHeight: '1.6' }}>$</span>
            <span style={{
              display: 'inline-block',
              width: '9px',
              height: '18px',
              background: 'var(--neutral-0)',
              marginLeft: '6px',
              animation: 'cursor-blink 1s infinite',
              verticalAlign: 'middle'
            }} />
          </div>
        )}
      </div>
    </div>
  );
}
