import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { LayoutDashboard, TrendingUp, DollarSign, Wallet, Coins } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [chartView, setChartView] = useState('type'); // 'type' or 'stock'
    const [tableCurrency, setTableCurrency] = useState('original'); // 'original' or 'krw'

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 60000); // Auto-refresh every 1 min
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/dashboard/summary`);
            setData(res.data);
            setError(null);
        } catch (err) {
            console.error("Fetch error:", err);
            setError("Failed to fetch data.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="flex items-center justify-center h-screen font-medium text-gray-500">Loading Dashboard...</div>;
    if (error) return <div className="flex items-center justify-center h-screen text-red-500 font-semibold">{error}</div>;
    if (!data) return null;

    const { summary, holdings } = data;

    // 1. Data by Individual Stocks
    const stockData = [
        ...holdings.overseas.map(h => ({ ...h, value_krw: h.current_price * h.quantity * 1200 })),
        ...holdings.domestic.map(h => ({ ...h, value_krw: h.current_price * h.quantity }))
    ].filter(a => a.value_krw > 0).sort((a, b) => b.value_krw - a.value_krw);

    const topStocks = stockData.slice(0, 7).map(s => ({ name: s.name, value: s.value_krw, color: s.currency === 'USD' ? '#8b5cf6' : '#3b82f6' }));
    if (stockData.length > 7) {
        const otherValue = stockData.slice(7).reduce((acc, curr) => acc + curr.value_krw, 0);
        topStocks.push({ name: 'Others', value: otherValue, color: '#94a3b8' });
    }

    // 2. Data by Asset Type
    const typeData = [
        { name: 'Domestic', value: summary.domestic.total_eval_krw, color: '#3b82f6' },
        { name: 'Overseas', value: summary.overseas.total_eval_krw, color: '#8b5cf6' }
    ].filter(item => item.value > 0);

    const currentChartData = chartView === 'type' ? typeData : topStocks;

    const formatKRW = (val) => new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(val);
    const formatUSD = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
                    <LayoutDashboard size={32} className="text-blue-600" />
                    Asset Dashboard
                </h1>
                <div className="text-sm text-gray-500">
                    Last Updated: {new Date().toLocaleTimeString()}
                </div>
            </header>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <SummaryCard
                    title="Total Assets (KRW)"
                    value={formatKRW(summary.total_asset_krw)}
                    icon={<Wallet size={24} />}
                    bg="bg-gradient-to-br from-indigo-600 to-blue-700"
                />
                <SummaryCard
                    title="Total Profit/Loss"
                    value={formatKRW(summary.total_pl_krw)}
                    isProfit={summary.total_pl_krw >= 0}
                    icon={<TrendingUp size={24} />}
                    bg="bg-gradient-to-br from-orange-400 to-rose-500"
                    textColor="text-white"
                />
                <SummaryCard
                    title="Overseas (USD)"
                    value={formatUSD(summary.overseas.total_eval_usd)}
                    sub={`Return: ${summary.overseas.return_rate.toFixed(2)}%`}
                    icon={<DollarSign size={24} />}
                    bg="bg-gradient-to-br from-fuchsia-600 to-purple-700"
                />
                <SummaryCard
                    title="Domestic (KRW)"
                    value={formatKRW(summary.domestic.total_eval_krw)}
                    sub={`Return: ${summary.domestic.return_rate.toFixed(2)}%`}
                    icon={<Coins size={24} />}
                    bg="bg-gradient-to-br from-emerald-500 to-teal-700"
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Asset Allocation Chart */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-1 h-fit">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-gray-700">Allocation</h2>
                        <div className="flex bg-gray-100 p-1 rounded-lg">
                            <button
                                onClick={() => setChartView('type')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${chartView === 'type' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-800'}`}
                            >
                                Type
                            </button>
                            <button
                                onClick={() => setChartView('stock')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${chartView === 'stock' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-800'}`}
                            >
                                Stock
                            </button>
                        </div>
                    </div>

                    <div className="h-72 flex flex-col items-center justify-center">
                        {currentChartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={currentChartData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={70}
                                        outerRadius={90}
                                        paddingAngle={2}
                                        dataKey="value"
                                        nameKey="name"
                                    >
                                        {currentChartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color || '#3b82f6'} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value) => formatKRW(value)} />
                                    <Legend
                                        verticalAlign="bottom"
                                        align="center"
                                        layout="horizontal"
                                        iconType="circle"
                                        wrapperStyle={{ paddingTop: '20px', fontSize: '11px' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-gray-400 text-sm">No assets found.</div>
                        )}
                    </div>
                </div>

                {/* Holdings Table */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-2 flex flex-col max-h-[600px]">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-gray-700">Holdings</h2>
                        <div className="flex bg-gray-100 p-1 rounded-lg">
                            <button
                                onClick={() => setTableCurrency('original')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${tableCurrency === 'original' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-800'}`}
                            >
                                Original
                            </button>
                            <button
                                onClick={() => setTableCurrency('krw')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${tableCurrency === 'krw' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-800'}`}
                            >
                                KRW Only
                            </button>
                        </div>
                    </div>

                    <div className="overflow-x-auto overflow-y-auto flex-1 pr-2">
                        <table className="w-full text-left border-collapse">
                            <thead className="sticky top-0 bg-white z-10 shadow-[0_1px_0_0_rgba(0,0,0,0.05)]">
                                <tr className="text-gray-600 uppercase text-[10px] tracking-wider font-bold">
                                    <th className="px-4 py-3">Symbol</th>
                                    <th className="px-4 py-3">Name</th>
                                    <th className="px-4 py-3 text-right">Qty</th>
                                    <th className="px-4 py-3 text-right">Price</th>
                                    <th className="px-4 py-3 text-right">Eval Value</th>
                                    <th className="px-4 py-3 text-right">Return</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 text-sm">
                                {stockData.map((item, idx) => {
                                    const evalValue = item.current_price * item.quantity;
                                    return (
                                        <tr key={idx} className="hover:bg-blue-50/50 transition-colors group">
                                            <td className="px-4 py-4 font-bold text-gray-900">{item.symbol}</td>
                                            <td className="px-4 py-4 text-gray-500 truncate max-w-[140px]" title={item.name}>{item.name}</td>
                                            <td className="px-4 py-4 text-right font-mono text-gray-600">{item.quantity.toLocaleString()}</td>
                                            <td className="px-4 py-4 text-right font-mono text-gray-800">
                                                {tableCurrency === 'original'
                                                    ? (item.currency === 'USD' ? formatUSD(item.current_price) : formatKRW(item.current_price))
                                                    : formatKRW(item.currency === 'USD' ? item.current_price * 1200 : item.current_price)
                                                }
                                            </td>
                                            <td className="px-4 py-4 text-right font-mono font-semibold text-blue-700">
                                                {tableCurrency === 'original'
                                                    ? (item.currency === 'USD' ? formatUSD(evalValue) : formatKRW(evalValue))
                                                    : formatKRW(item.currency === 'USD' ? evalValue * 1200 : evalValue)
                                                }
                                            </td>
                                            <td className={`px-4 py-4 text-right font-bold text-xs ${item.return_rate >= 0 ? 'text-green-600' : 'text-rose-500'}`}>
                                                {item.return_rate >= 0 ? '+' : ''}{item.return_rate.toFixed(2)}%
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

function SummaryCard({ title, value, sub, icon, bg, isProfit, textColor = "text-white" }) {
    return (
        <div className={`${bg} p-6 rounded-xl shadow-sm border border-gray-100 relative overflow-visible transition-all`}>
            <div className="flex justify-between items-start gap-4">
                <div className="z-10 flex-1 min-w-0">
                    <h3 className={`text-sm font-medium opacity-90 ${textColor === "text-white" ? "text-blue-50" : "text-gray-500"}`}>{title}</h3>
                    <p className={`text-2xl font-bold mt-1 break-words ${textColor}`}>
                        {value}
                    </p>
                    {sub && <p className={`text-xs mt-1 font-medium opacity-90 ${textColor}`}>{sub}</p>}
                </div>
                <div className={`p-2 rounded-lg flex-shrink-0 bg-white/20 ${textColor}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
