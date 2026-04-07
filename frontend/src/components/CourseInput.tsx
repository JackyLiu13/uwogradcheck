"use client";
import { useState } from 'react';

export default function CourseInput({ courses, onChange }: { courses: string[], onChange: (c: string[]) => void }) {
  const [input, setInput] = useState(courses.join(', '));

  const handleUpdate = () => {
    // split by comma or newline
    const parsed = input
      .split(/,|\n/)
      .map(s => s.trim().toUpperCase())
      .filter(s => s.length > 0);
    
    onChange(parsed);
  };

  return (
    <div className="glass-panel">
      <h3 className="mb-2">2. Enter your Transcript</h3>
      <p className="text-muted mb-2" style={{ fontSize: '0.9rem' }}>
        Paste your completed courses separated by commas or newlines (e.g. CALCULUS 1000A, MATH 1600).
      </p>
      
      <textarea 
        rows={3}
        placeholder="COMPSCI 1026A, COMPSCI 1027B..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onBlur={handleUpdate}
        style={{ resize: 'vertical' }}
      />
      
      <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {courses.map((c, i) => (
          <span key={i} className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{c}</span>
        ))}
      </div>
    </div>
  );
}
