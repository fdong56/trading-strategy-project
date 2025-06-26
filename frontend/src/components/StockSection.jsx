import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

const API_URL = import.meta.env.VITE_API_URL;

export default function StockSection({ config, handleConfigChange }) {
  const [stockSymbols, setStockSymbols] = useState([]);
  const [priceData, setPriceData] = useState(null);

  const minDate = '2000-02-01';
  const maxDate = '2012-09-12';

  useEffect(() => {
    // Hardcoded list of stock symbols
    const symbols = [
      "A", "AA", "AAPL", "ABC", "ABKFQ", "ABT", "ACAS", "ACE", "ADBE", "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AET", "AFL", "AGN", "AIG", "AIV", "AKAM", "ALL", "ALTR", "AMAT", "AMD", "AMGN", "AMT", "AMZN", "AN", "ANF", "AON", "APA", "APC", "APD", "APOL", "ASH", "ATI", "AVB", "AVP", "AVY", "AXP", "AZO", "BA", "BAC", "BAX", "BBBY", "BBT", "BBY", "BC", "BCR", "BDX", "BEAM", "BEN", "BHI", "BIG", "BIIB", "BK", "BLL", "BMC", "BMS", "BMY", "BRCM", "BRLI", "BSX", "BXP", "C", "CA", "CAG", "CAH", "CAT", "CB", "CBE", "CBSH", "CCE", "CCL", "CELG", "CHK", "CHRW", "CI", "CIEN", "CINF", "CL", "CLX", "CMA", "CMCSA", "CMI", "CMS", "CNP", "CNX", "COF", "COP", "COST", "CPB", "CPWR", "CSC", "CSCO", "CSX", "CTAS", "CTL", "CTSH", "CTXS", "CVG", "CVH", "CVS", "CVX", "D", "DD", "DDR", "DDS", "DE", "DELL", "DGX", "DHI", "DHR", "DIS", "DOV", "DOW", "DRI", "DTE", "DUK", "DVN", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMC", "EMN", "EMR", "EOG", "EQR", "ESRX", "ESV", "ETFC", "ETN", "ETR", "EXC", "EXPD", "F", "FCX", "FDO", "FDX", "FE", "FHN", "FII", "FISV", "FITB", "FMCC", "FNMA", "FRX", "FTR", "GAS", "GCI", "GD", "GE", "GILD", "GIS", "GLW", "GPC", "GPS", "GS", "GT", "GWW", "HAL", "HAR", "HAS", "HBAN", "HCBK", "HD", "HES", "HIG", "HNZ", "HOG", "HON", "HOT", "HPQ", "HRB", "HST", "HSY", "HUM", "IACI", "IBM", "IFF", "IGT", "INTC", "INTU", "IP", "IPG", "IR", "ITT", "ITW", "JBL", "JCI", "JCP", "JDSU", "JEC", "JNJ", "JNPR", "JNY", "JPM", "JWN", "K", "KBH", "KEY", "KIM", "KLAC", "KMB", "KO", "KR", "KSS", "L", "LEG", "LEN", "LH", "LLL", "LLTC", "LLY", "LM", "LMT", "LNC", "LOW", "LSI", "LTD", "LUK", "LUV", "LXK", "M", "MAR", "MAS", "MAT", "MBI", "MCD", "MCHP", "MCK", "MDP", "MDT", "MHP", "MIL", "MKC", "MMC", "MMM", "MO", "MOLX", "MRK", "MRO", "MS", "MSFT", "MSI", "MTB", "MTG", "MTW", "MU", "MUR", "MWV", "MWW", "MYL", "NBL", "NBR", "NE", "NEE", "NEM", "NI", "NKE", "NOC", "NOV", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NWL", "NWSA", "NYT", "ODP", "OMC", "OMX", "ORCL", "OXY", "PAYX", "PBI", "PCAR", "PCG", "PCL", "PCP", "PDCO", "PEP", "PFE", "PG", "PGR", "PH", "PHM", "PKI", "PLD", "PLL", "PNC", "PNW", "POM", "PPG", "PPL", "PSA", "PX", "QCOM", "QLGC", "R", "RAI", "RDC", "RF", "RHI", "RIG", "RL", "ROK", "RRC", "RRD", "RSH", "RTN", "S", "SBUX", "SCHW", "SEE", "SHW", "SIAL", "SLB", "SLM", "SNA", "SNDK", "SNV", "SO", "SPG", "SPLS", "SPY", "SRE", "SSP", "STI", "STJ", "STR", "STT", "STZ", "SUN", "SVU", "SWK", "SWY", "SYK", "SYMC", "SYY", "T", "TAP", "TE", "TEG", "TER", "TEX", "TGT", "THC", "TIE", "TIF", "TJX", "TLAB", "TMK", "TMO", "TROW", "TRV", "TSN", "TSO", "TWX", "TXN", "TXT", "TYC", "UIS", "UNH", "UNM", "UNP", "UPS", "USB", "UTX", "VAR", "VFC", "VLO", "VMC", "VNO", "VRSN", "VZ", "WAG", "WAT", "WEN", "WFC", "WFM", "WFR", "WFT", "WHR", "WM", "WMB", "WMT", "WPI", "WPO", "WY", "X", "XEL", "XL", "XLNX", "XOM", "XRX", "YHOO", "YUM", "ZION"
    ];
    setStockSymbols(symbols);
  }, []);

  useEffect(() => {
    if (config.symbol) {
      fetch(`${API_URL}/api/price?symbol=${config.symbol}&start_date=${minDate}&end_date=${maxDate}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch price data');
          return res.json();
        })
        .then(data => setPriceData(data))
        .catch(() => setPriceData(null));
    }
  }, [config.symbol]);

  return (
    <div className="stock-section">
      <h3>📈 Stock</h3>
      <label htmlFor="symbol">Stock Symbol</label>
      <select
        id="symbol"
        value={config.symbol}
        onChange={e => handleConfigChange('symbol', e.target.value)}
        required
      >
        <option value="">Select a symbol</option>
        {stockSymbols.map(sym => (
          <option key={sym} value={sym}>{sym}</option>
        ))}
      </select>
      
      {priceData && priceData.dates && priceData.prices && (
        <div style={{ marginTop: 16, marginBottom: 16, border: '1px solid #ccc', borderRadius: '8px' }}>
          {priceData ? (
            <Line
              data={{
                labels: priceData.dates,
                datasets: [
                  {
                    label: `${config.symbol} Price`,
                    data: priceData.prices,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.1,
                    pointRadius: 0
                  }
                ]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false },
                  title: { display: true }
                },
                scales: {
                  y: {
                    title: { display: true, text: 'Adjusted Price' },
                    grid: { display: true }
                  },
                  x: {
                    title: { display: true },
                    grid: { display: false },
                    ticks: {
                      callback: function(value) {
                        const date = this.getLabelForValue(value);
                        return date;
                      }
                    }
                  }
                }
              }}
            />
          ) : (
            <div className="chart-placeholder" title="Stock Price Chart"></div>
          )}
        </div>
      )}
      <div className="date-row">
        <div>
          <label htmlFor="impact">Impact</label>
          <input
            type="text"
            id="impact"
            placeholder="e.g. 0.005"
            value={config.impact}
            onChange={e => handleConfigChange('impact', e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="commission">Commission</label>
          <input
            type="text"
            id="commission"
            placeholder="e.g. 9.95"
            value={config.commission}
            onChange={e => handleConfigChange('commission', e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="start-value">Start Value</label>
          <input
            type="text"
            id="start-value"
            placeholder="e.g. 100000"
            value={config.start_val}
            onChange={e => handleConfigChange('start_val', e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}