"use client";

export default function EvaluationResults({ result }: { result: any }) {
  const progressPercent = result.progress_percentage || 0;
  const admission = result.admission;
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Unrecognized Courses Warning */}
      {result.invalid_courses && result.invalid_courses.length > 0 && (
        <div style={{ 
          padding: '16px', 
          background: 'rgba(255, 60, 60, 0.1)', 
          borderLeft: '4px solid var(--danger)', 
          borderRadius: '0 8px 8px 0',
          marginBottom: '8px'
        }}>
          <h4 style={{ color: '#ffb3b3', margin: '0 0 8px 0', fontSize: '1rem' }}>
            Unrecognized Courses Ignored
          </h4>
          <p style={{ margin: '0 0 12px 0', fontSize: '0.85rem', color: 'rgba(255,255,255,0.8)' }}>
            The following courses were not recognized as valid Western courses and have been ignored:
          </p>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {result.invalid_courses.map((c: string, i: number) => (
              <span key={i} className="badge badge-danger">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Admission Requirements — Structured Groups */}
      {admission && admission.groups && admission.groups.length > 0 && (
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h3 className="mb-3">Admission Requirements</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {admission.groups.map((g: any, i: number) => {
              const hasMet = g.courses_met && g.courses_met.length > 0;
              const isSatisfied = g.type === 'required' 
                ? g.courses_missing.length === 0
                : hasMet;
              
              return (
                <div key={i} style={{
                  padding: '14px 16px',
                  background: isSatisfied ? 'var(--success-glass)' : 'rgba(0,0,0,0.2)',
                  borderLeft: `4px solid ${isSatisfied ? 'var(--success)' : 'rgba(255,255,255,0.15)'}`,
                  borderRadius: '0 8px 8px 0'
                }}>
                  {/* Header row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div>
                      <span style={{ fontWeight: 600 }}>{g.credits} credit{g.credits !== 1 ? 's' : ''}</span>
                      <span className="text-muted" style={{ fontSize: '0.85rem', marginLeft: '6px' }}>
                        {g.type === 'choose_from' ? '— choose from:' : '— required:'}
                      </span>
                    </div>
                    {g.grade_requirement && (
                      <span className="badge" style={{ background: 'rgba(255,204,0,0.15)', color: '#ffcc00', fontSize: '0.75rem' }}>
                        Min {g.grade_requirement}%
                      </span>
                    )}
                  </div>
                  
                  {/* Course list */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {g.courses_met.map((c: string, idx: number) => (
                      <div key={`met-${idx}`} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--success)' }}>✓</span>
                        <span>{c}</span>
                      </div>
                    ))}
                    {g.courses_missing.map((c: string, idx: number) => (
                      <div key={`miss-${idx}`} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--text-muted)', opacity: 0.4 }}>○</span>
                        <span className="text-muted">{c}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
          
          <div style={{ marginTop: '16px', fontSize: '0.8rem', color: '#ffcc00', padding: '8px 10px', background: 'rgba(255,204,0,0.08)', borderRadius: '6px', lineHeight: '1.5' }}>
            <strong>Note:</strong> Admission requirements may vary by calendar year. 
            Confirm with your academic advisor for your specific admission year.
          </div>
        </div>
      )}

      {/* Module Credits Progress Section */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '8px' }}>
          <h3>Module Credits Progress</h3>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: progressPercent >= 100 ? 'var(--success)' : 'var(--primary)' }}>
            {progressPercent.toFixed(1)}%
          </div>
        </div>
        
        <div className="progress-bg">
          <div className="progress-fill" style={{ width: `${Math.min(100, progressPercent)}%` }}></div>
        </div>
        
        <p className="text-muted mb-4">
          {result.total_credits_met} out of {result.total_credits_required} module credits completed for <strong>{result.module_name}</strong>.
        </p>
        
        <h4 className="mb-2">Requirements Breakdown</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {result.groups.map((g: any, i: number) => {
             const met = g.is_met;
             return (
               <div key={i} style={{ 
                 padding: '16px', 
                 background: met ? 'var(--success-glass)' : 'rgba(0,0,0,0.2)',
                 borderLeft: `4px solid ${met ? 'var(--success)' : 'var(--danger)'}`,
                 borderRadius: '0 8px 8px 0'
               }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                   <strong style={{ textTransform: 'capitalize' }}>
                     {g.type.replace('_', ' ')} Requirement
                   </strong>
                   <span className={met ? 'text-success' : 'text-danger'} style={{ fontSize: '0.9rem', fontWeight: 600 }}>
                     {g.credits_met} / {g.credits_required} cr
                   </span>
                 </div>

                 {g.courses_met && g.courses_met.length > 0 && (
                   <div style={{ marginBottom: '8px' }}>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                       {g.courses_met.map((c: string, idx: number) => (
                         <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                           <span style={{ color: 'var(--success)' }}>✓</span>
                           <span>{c}</span>
                         </div>
                       ))}
                     </div>
                   </div>
                 )}
                 
                 {g.description && <p className="text-muted mb-2" style={{ fontSize: '0.9rem' }}>{g.description}</p>}
                 
                 {g.courses_missing && g.courses_missing.length > 0 && (
                   <div style={{ marginTop: '8px' }}>
                     <span style={{ fontSize: '0.85rem', color: '#ffb3b3', display: 'block', marginBottom: '4px' }}>Still needed:</span>
                     <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                       {g.courses_missing.slice(0, 10).map((c: string, idx: number) => (
                         <span key={idx} className="badge badge-danger">{c}</span>
                       ))}
                       {g.courses_missing.length > 10 && <span className="badge" style={{background: 'transparent', color: 'var(--text-muted)'}}>+{g.courses_missing.length - 10} more</span>}
                     </div>
                   </div>
                 )}
                 
                 {g.notes && (
                   <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#ffcc00', padding: '6px 8px', background: 'rgba(255,204,0,0.1)', borderRadius: '4px' }}>
                     <strong>Notice:</strong> {g.notes}
                   </div>
                 )}
               </div>
             );
          })}
        </div>
      </div>
    </div>
  );
}
