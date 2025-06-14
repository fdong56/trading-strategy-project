import React, { useState, useEffect } from 'react';

export default function ValidationSection({ config }) {
  
  const [valStartDate, setValStartDate] = useState('2009-01-01');
  const [valEndDate, setValEndDate] = useState('2010-01-01');

  // Ensure validation dates are within training period
  const minDate = '2000-02-01';
  const maxDate = '2012-09-12';

  return (
    <div className="validation-section">
      <h3>📈 Validation</h3>
      <div className="date-row">
        <div>
          <label htmlFor="val_start">Validation Start Date</label>
          <input
            type="date"
            id="val_start"
            value={valStartDate}
            min={minDate}
            max={valEndDate}
            onChange={e => setValStartDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="val_end">Validation End Date</label>
          <input
            type="date"
            id="val_end"
            value={valEndDate}
            min={valStartDate}
            max={maxDate}
            onChange={e => setValEndDate(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}