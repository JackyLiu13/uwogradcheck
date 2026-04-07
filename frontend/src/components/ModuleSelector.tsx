"use client";
import { useState, useEffect, useRef } from 'react';

type Module = {
  id: string;
  name: string;
  type: string;
  faculty: string;
};

export default function ModuleSelector({ selectedId, onSelect }: { selectedId: string, onSelect: (id: string) => void }) {
  const [modules, setModules] = useState<Module[]>([]);
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/modules')
      .then(res => res.json())
      .then(data => setModules(data.modules || []))
      .catch(err => console.error("Failed to load modules", err));
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filtered = modules.filter(m => 
    m.name.toLowerCase().includes(query.toLowerCase()) || 
    m.faculty.toLowerCase().includes(query.toLowerCase())
  ).slice(0, 50);

  const selectedModule = modules.find(m => m.id === selectedId);

  return (
    <div className="glass-panel" ref={containerRef}>
      <h3 className="mb-2">1. Select your Degree Module</h3>
      <div className="dropdown-container">
        <input 
          type="text" 
          placeholder="Search for an honors specialization, major..." 
          value={open ? query : (selectedModule ? selectedModule.name : query)}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!open) setOpen(true);
            if (e.target.value === '') onSelect('');
          }}
          onFocus={() => { setOpen(true); setQuery(''); }}
        />
        
        {open && (
          <div className="dropdown-list">
            {filtered.length === 0 ? (
              <div className="dropdown-item text-muted">No modules found. Try a different term.</div>
            ) : (
              filtered.map(m => (
                <div 
                  key={m.id} 
                  className="dropdown-item"
                  onClick={() => {
                    onSelect(m.id);
                    setQuery('');
                    setOpen(false);
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{m.name}</div>
                  <div className="text-muted" style={{ fontSize: '0.8rem' }}>{m.faculty} • {m.type}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      {selectedModule && !open && (
        <div style={{ marginTop: '12px' }}>
          <span className="badge badge-primary">{selectedModule.type}</span>
          <span className="text-muted" style={{ fontSize: '0.85rem', marginLeft: '8px' }}>{selectedModule.faculty}</span>
        </div>
      )}
    </div>
  );
}
