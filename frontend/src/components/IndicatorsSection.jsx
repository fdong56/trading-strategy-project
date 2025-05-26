import React from 'react';

export default function IndicatorsSection({ selectedIndicators, indicatorParams, handleIndicatorSelect, handleIndicatorParamChange, INDICATOR_OPTIONS }) {
  return (
    <div className="indicators-section">
      <h3>📊 Indicators</h3>
      {[0, 1, 2].map(idx => (
        <div key={idx} style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: 'bold', fontSize: '1.08rem', color: '#1f2937' }}>Select Indicator {idx + 1}</label>
          <select
            value={selectedIndicators[idx]}
            onChange={e => handleIndicatorSelect(idx, e.target.value)}
            required
          >
            <option value="">Select indicator</option>
            {INDICATOR_OPTIONS.filter(opt => !selectedIndicators.includes(opt.key) || selectedIndicators[idx] === opt.key).map(opt => (
              <option key={opt.key} value={opt.key}>{opt.label}</option>
            ))}
          </select>
          {selectedIndicators[idx] && (() => {
            const params = INDICATOR_OPTIONS.find(opt => opt.key === selectedIndicators[idx]).params;
            const rows = [];
            for (let i = 0; i < params.length; i += 3) {
              rows.push(
                <div className="date-row" key={`indi-row-${idx}-${i}`}>
                  {params.slice(i, i + 3).map(param => (
                    <div key={param.key} style={{ marginLeft: 12 }}>
                      <label style={{ fontStyle: 'italic', fontWeight: 'normal' }}>{param.label}</label>
                      <input
                        className="param-input"
                        type={param.type}
                        placeholder={param.placeholder}
                        value={indicatorParams[selectedIndicators[idx]]?.[param.key] || ''}
                        onChange={e => handleIndicatorParamChange(selectedIndicators[idx], param.key, e.target.value)}
                        required
                      />
                    </div>
                  ))}
                </div>
              );
            }
            return rows;
          })()}
        </div>
      ))}
    </div>
  );
} 