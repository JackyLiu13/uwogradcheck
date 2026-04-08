"use client";

export default function EvaluationResults({ result }: { result: any }) {
  const progressPercent = result.progress_percentage || 0;
  const admission = result.admission;
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Admission Requirements Section */}
      {admission && (
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '8px' }}>
            <h3>Admission Requirements</h3>
            <span className={admission.is_met ? 'badge badge-success' : 'badge badge-danger'}>
              {admission.is_met ? 'MET' : `${admission.courses_met.length} / ${admission.total_courses} completed`}
            </span>
          </div>
          
          <p className="text-muted mb-3" style={{ fontSize: '0.85rem', lineHeight: '1.5' }}>
            These are the prerequisite courses needed for admission into the module.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {admission.courses_met.map((c: string, i: number) => (
              <div key={`met-${i}`} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--success)', fontSize: '1.1rem' }}>✓</span>
                <span>{c}</span>
              </div>
            ))}
            {admission.courses_missing.map((c: string, i: number) => (
              <div key={`miss-${i}`} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--danger)', fontSize: '1.1rem' }}>✗</span>
                <span style={{ color: 'var(--text-muted)' }}>{c}</span>
              </div>
            ))}
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

                 {/* Show completed courses with checkmarks */}
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
