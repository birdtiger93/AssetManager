import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PeriodReturnsChart.css';

export default function PeriodReturnsChart() {
    const [period, setPeriod] = useState('1M');
    const [groupBy, setGroupBy] = useState('total');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showKospi, setShowKospi] = useState(true);
    const [showSp500, setShowSp500] = useState(true);
    const [showNasdaq, setShowNasdaq] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`/api/returns/period?period=${period}&group_by=${groupBy}&benchmark=both`)
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching returns:', err);
                setLoading(false);
            });
    }, [period, groupBy]);

    if (loading) {
        return <div className="period-returns-loading">Loading...</div>;
    }

    if (!data || !data.daily_series || data.daily_series.length === 0) {
        return (
            <div className="period-returns-card">
                <h3>Period Returns vs Benchmarks</h3>
                <p>No data available for the selected period.</p>
            </div>
        );
    }

    const portfolio = data.portfolio || {};
    const benchmarks = data.benchmarks || {};
    const breakdown = data.breakdown || [];

    return (
        <div className="period-returns-card">
            <div className="period-returns-header">
                <h3>Period Returns vs Benchmarks</h3>
                <div className="period-selector">
                    {['1D', '1W', '1M', '3M', 'YTD', '1Y'].map(p => (
                        <button
                            key={p}
                            className={period === p ? 'active' : ''}
                            onClick={() => setPeriod(p)}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            <div className="returns-summary">
                <div className="summary-item portfolio">
                    <span className="label">My Portfolio</span>
                    <span className="value" style={{ color: portfolio.return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                        {portfolio.return_pct?.toFixed(2)}%
                    </span>
                    <span className="amount">
                        {portfolio.profit_loss >= 0 ? '+' : ''}
                        ₩{(portfolio.profit_loss || 0).toLocaleString()}
                    </span>
                </div>

                {benchmarks.kospi && (
                    <div className="summary-item kospi">
                        <span className="label">KOSPI</span>
                        <span className="value" style={{ color: benchmarks.kospi.return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                            {benchmarks.kospi.return_pct?.toFixed(2)}%
                        </span>
                    </div>
                )}

                {benchmarks.sp500 && (
                    <div className="summary-item sp500">
                        <span className="label">S&P 500</span>
                        <span className="value" style={{ color: benchmarks.sp500.return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                            {benchmarks.sp500.return_pct?.toFixed(2)}%
                        </span>
                    </div>
                )}

                {benchmarks.nasdaq && (
                    <div className="summary-item nasdaq">
                        <span className="label">NASDAQ</span>
                        <span className="value" style={{ color: benchmarks.nasdaq.return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                            {benchmarks.nasdaq.return_pct?.toFixed(2)}%
                        </span>
                    </div>
                )}

                {benchmarks.kospi && (
                    <div className="summary-item alpha">
                        <span className="label">Alpha vs KOSPI</span>
                        <span className="value" style={{ color: (portfolio.return_pct - benchmarks.kospi.return_pct) >= 0 ? '#10b981' : '#ef4444' }}>
                            {(portfolio.return_pct - benchmarks.kospi.return_pct).toFixed(2)}%
                        </span>
                    </div>
                )}
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={data.daily_series}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                            dataKey="date"
                            stroke="#9ca3af"
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis
                            stroke="#9ca3af"
                            tick={{ fontSize: 12 }}
                            label={{ value: 'Return %', angle: -90, position: 'insideLeft', style: { fill: '#9ca3af' } }}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem' }}
                            labelStyle={{ color: '#f3f4f6' }}
                        />
                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="portfolio_return"
                            stroke="#8b5cf6"
                            strokeWidth={3}
                            dot={false}
                            connectNulls
                            name="My Portfolio"
                        />

                        {showKospi && data.daily_series.some(d => d.kospi_return !== undefined) && (
                            <Line
                                type="monotone"
                                dataKey="kospi_return"
                                stroke="#ef4444"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                                connectNulls
                                name="KOSPI"
                            />
                        )}

                        {showSp500 && data.daily_series.some(d => d.sp500_return !== undefined) && (
                            <Line
                                type="monotone"
                                dataKey="sp500_return"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                                connectNulls
                                name="S&P 500"
                            />
                        )}

                        {showNasdaq && data.daily_series.some(d => d.nasdaq_return !== undefined) && (
                            <Line
                                type="monotone"
                                dataKey="nasdaq_return"
                                stroke="#8b5cf6" // Violet/Purple
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                                connectNulls
                                name="NASDAQ"
                            />
                        )}
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="chart-controls">
                <label>
                    <input
                        type="checkbox"
                        checked={showKospi}
                        onChange={e => setShowKospi(e.target.checked)}
                    />
                    <span>KOSPI</span>
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked={showSp500}
                        onChange={e => setShowSp500(e.target.checked)}
                    />
                    <span>S&P 500</span>
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked={showNasdaq}
                        onChange={e => setShowNasdaq(e.target.checked)}
                    />
                    <span>NASDAQ</span>
                </label>
            </div>

            {
                groupBy !== 'total' && breakdown.length > 0 && (
                    <div className="breakdown-section">
                        <h4>Breakdown</h4>
                        <table className="breakdown-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Start Value</th>
                                    <th>End Value</th>
                                    <th>Return</th>
                                </tr>
                            </thead>
                            <tbody>
                                {breakdown.slice(0, 5).map((item, idx) => (
                                    <tr key={idx}>
                                        <td>{item.name}</td>
                                        <td>₩{item.start_value?.toLocaleString()}</td>
                                        <td>₩{item.end_value?.toLocaleString()}</td>
                                        <td style={{ color: item.return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                                            {item.return_pct?.toFixed(2)}%
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )
            }

            <div className="group-by-selector">
                <span>Group by:</span>
                <label>
                    <input
                        type="radio"
                        name="groupBy"
                        value="total"
                        checked={groupBy === 'total'}
                        onChange={e => setGroupBy(e.target.value)}
                    />
                    <span>Total</span>
                </label>
                <label>
                    <input
                        type="radio"
                        name="groupBy"
                        value="instrument"
                        checked={groupBy === 'instrument'}
                        onChange={e => setGroupBy(e.target.value)}
                    />
                    <span>Instrument</span>
                </label>
                <label>
                    <input
                        type="radio"
                        name="groupBy"
                        value="brokerage"
                        checked={groupBy === 'brokerage'}
                        onChange={e => setGroupBy(e.target.value)}
                    />
                    <span>Brokerage</span>
                </label>
            </div>
        </div >
    );
}
