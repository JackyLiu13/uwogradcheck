"use client";

import { useState, useEffect } from 'react';
import ModuleSelector from '@/components/ModuleSelector';
import CourseInput from '@/components/CourseInput';
import EvaluationResults from '@/components/EvaluationResults';

export default function Home() {
  const [selectedModuleId, setSelectedModuleId] = useState<string>('');
  const [studentCourses, setStudentCourses] = useState<string[]>([]);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchEvaluation = async () => {
    if (!selectedModuleId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: selectedModuleId,
          student_courses: studentCourses
        })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || 'Failed to evaluate');
      
      setEvaluation(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedModuleId) {
      fetchEvaluation();
    }
  }, [selectedModuleId, studentCourses]);

  return (
    <main className="container">
      <div className="header animate-fade-in">
        <h1>Graduation Checker</h1>
        <p>Western University • Verify your module requirements</p>
      </div>
      
      <div className="grid-2 mb-4 animate-fade-in delay-100">
        <ModuleSelector 
          selectedId={selectedModuleId} 
          onSelect={setSelectedModuleId} 
        />
        
        <CourseInput 
          courses={studentCourses} 
          onChange={setStudentCourses} 
        />
      </div>

      {error && (
        <div className="glass-panel text-danger mb-4 animate-fade-in">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="glass-panel mb-4 animate-fade-in text-center text-muted">
          <p>Evaluating transcript...</p>
        </div>
      )}

      {evaluation && !loading && (
        <div className="animate-fade-in delay-200">
           <EvaluationResults result={evaluation} />
        </div>
      )}
    </main>
  );
}
