import React, { useState } from 'react';
import axios from 'axios';
import { DollarSign, Send } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

const Trade = () => {
    const [formData, setFormData] = useState({
        asset_type: "OVERSEAS",
        symbol: "",
        side: "BUY",
        quantity: 0,
        price: 0,
        exchange: "NASD"
    });
    const [status, setStatus] = useState({ type: '', msg: '' });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus({ type: '', msg: '' });

        try {
            const payload = {
                ...formData,
                quantity: Number(formData.quantity),
                price: Number(formData.price)
            };

            const res = await axios.post(`${API_BASE}/api/trade/order`, payload);
            setStatus({ type: 'success', msg: `Order Successful: ${res.data.message}` });
        } catch (err) {
            const errMsg = err.response?.data?.detail || err.message;
            setStatus({ type: 'error', msg: `Order Failed: ${errMsg}` });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                <header className="mb-8 flex items-center gap-3 border-b pb-4">
                    <DollarSign size={28} className="text-blue-600" />
                    <h1 className="text-2xl font-bold text-gray-800">Place Order</h1>
                </header>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Asset Type</label>
                            <select
                                name="asset_type"
                                value={formData.asset_type}
                                onChange={handleChange}
                                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="OVERSEAS">Overseas (USA)</option>
                                <option value="DOMESTIC">Domestic (Korea)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Side</label>
                            <select
                                name="side"
                                value={formData.side}
                                onChange={handleChange}
                                className={`w-full p-3 border border-gray-200 rounded-lg focus:ring-2 outline-none font-bold ${formData.side === 'BUY' ? 'text-red-600 bg-red-50' : 'text-blue-600 bg-blue-50'}`}
                            >
                                <option value="BUY">BUY (매수)</option>
                                <option value="SELL">SELL (매도)</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Symbol (Code)</label>
                            <input
                                type="text"
                                name="symbol"
                                value={formData.symbol}
                                onChange={handleChange}
                                placeholder={formData.asset_type === 'OVERSEAS' ? 'AAPL, TSLA...' : '005930...'}
                                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none uppercase"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Exchange (Overseas)</label>
                            <select
                                name="exchange"
                                value={formData.exchange}
                                onChange={handleChange}
                                disabled={formData.asset_type === 'DOMESTIC'}
                                className="w-full p-3 border border-gray-200 rounded-lg disabled:bg-gray-100"
                            >
                                <option value="NASD">NASDAQ</option>
                                <option value="NYSE">NYSE</option>
                                <option value="AMEX">AMEX</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                            <input
                                type="number"
                                name="quantity"
                                value={formData.quantity}
                                onChange={handleChange}
                                min="1"
                                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Price (Limit)</label>
                            <input
                                type="number"
                                name="price"
                                value={formData.price}
                                onChange={handleChange}
                                step="0.01"
                                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                required
                            />
                            <p className="text-xs text-gray-500 mt-1">Set 0 for some market orders (Domestic)</p>
                        </div>
                    </div>

                    {status.msg && (
                        <div className={`p-4 rounded-lg ${status.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                            {status.msg}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-4 rounded-lg font-bold text-white flex justify-center items-center gap-2 transition-all
                            ${loading ? 'bg-gray-400' : (formData.side === 'BUY' ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600')}`}
                    >
                        <Send size={20} />
                        {loading ? 'Processing...' : `Submit ${formData.side} Order`}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Trade;
