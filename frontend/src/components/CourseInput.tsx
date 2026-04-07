"use client";
import { useState } from 'react';

export default function CourseInput({ courses, onChange }: { courses: string[], onChange: (c: string[]) => void }) {
  const [input, setInput] = useState(courses.join(', '));

  const handleSubmit = () => {
    const parsed = input
      .split(/,|\n/)
      .map(s => s.trim().toUpperCase())
      .filter(s => s.length > 0);
    
    onChange(parsed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="glass-panel">
      <h3 className="mb-2">2. Enter your Transcript</h3>
      <p className="text-muted mb-2" style={{ fontSize: '0.9rem' }}>
        List your completed courses separated by commas or newlines (e.g. COMPSCI 2208A, COMPSCI 2209B).
      </p>
      
      <textarea 
        rows={3}
        placeholder="COMPSCI 2208A, COMPSCI 2209B, COMPSCI 2210A..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onBlur={handleSubmit}
        onKeyDown={handleKeyDown}
        style={{ resize: 'vertical' }}
      />

      <button 
        onClick={handleSubmit}
        style={{ marginTop: '12px', width: '100%' }}
      >
        Evaluate Transcript
      </button>
      
      {courses.length > 0 && (
        <div style={{ marginTop: '12px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {courses.map((c, i) => (
            <span key={i} className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{c}</span>
          ))}
        </div>
      )}
    </div>
  );
}
