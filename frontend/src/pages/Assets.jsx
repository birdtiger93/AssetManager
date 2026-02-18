import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Plus, Trash2, TrendingUp, DollarSign, Edit2, X, Check } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

const Assets = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({
        asset_type: 'STOCK',
        name: '',
        symbol: '',
        quantity: '',
        buy_price: '',
        current_price: '',
        currency: 'KRW',
        brokerage: 'Manual'
    });

    useEffect(() => {
        fetchAssets();
    }, []);

    const fetchAssets = async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/assets/manual/`);
            setAssets(res.data);
        } catch (err) {
            console.error("Failed to fetch assets", err);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${API_BASE}/api/assets/manual/`, formData);
            setIsModalOpen(false);
            fetchAssets();
            setFormData({
                asset_type: 'STOCK',
                name: '',
                symbol: '',
                quantity: '',
                buy_price: '',
                current_price: '',
                currency: 'KRW',
                brokerage: 'Manual'
            });
        } catch (err) {
            console.error("Failed to create asset", err);
            alert("Failed to create asset");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this asset?")) return;
        try {
            await axios.delete(`${API_BASE}/api/assets/manual/${id}`);
            fetchAssets();
        } catch (err) {
            console.error("Failed to delete asset", err);
        }
    };

    const formatCurrency = (val, currency) => {
        return new Intl.NumberFormat(currency === 'USD' ? 'en-US' : 'ko-KR', {
            style: 'currency',
            currency: currency
        }).format(val);
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Assets...</div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
                    <TrendingUp size={32} className="text-blue-600" />
                    Manual Assets
                </h1>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
                >
                    <Plus size={20} />
                    Add Asset
                </button>
            </header>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-gray-50 border-b border-gray-100">
                            <tr className="text-xs uppercase text-gray-500 font-semibold tracking-wider">
                                <th className="px-6 py-4">Name</th>
                                <th className="px-6 py-4">Type</th>
                                <th className="px-6 py-4">Brokerage</th>
                                <th className="px-6 py-4 text-right">Quantity</th>
                                <th className="px-6 py-4 text-right">Avg Price</th>
                                <th className="px-6 py-4 text-right">Current Price</th>
                                <th className="px-6 py-4 text-right">Evaluation</th>
                                <th className="px-6 py-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {assets.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-8 text-center text-gray-400">
                                        No manual assets added yet.
                                    </td>
                                </tr>
                            ) : (
                                assets.map((asset) => (
                                    <tr key={asset.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="font-semibold text-gray-900">{asset.name}</div>
                                            <div className="text-xs text-gray-400">{asset.symbol}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                                                {asset.asset_type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {asset.brokerage}
                                        </td>
                                        <td className="px-6 py-4 text-right font-mono text-gray-600">
                                            {asset.quantity.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-right font-mono text-gray-600">
                                            {formatCurrency(asset.buy_price, asset.currency)}
                                        </td>
                                        <td className="px-6 py-4 text-right font-mono font-medium text-gray-900">
                                            {formatCurrency(asset.current_price, asset.currency)}
                                        </td>
                                        <td className="px-6 py-4 text-right font-mono font-bold text-blue-600">
                                            {formatCurrency(asset.current_price * asset.quantity, asset.currency)}
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <button
                                                onClick={() => handleDelete(asset.id)}
                                                className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                title="Delete"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <h3 className="text-lg font-bold text-gray-800">Add New Asset</h3>
                            <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Asset Type</label>
                                <select
                                    name="asset_type"
                                    value={formData.asset_type}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                >
                                    <option value="STOCK">Stock</option>
                                    <option value="CRYPTO">Crypto</option>
                                    <option value="REAL_ESTATE">Real Estate</option>
                                    <option value="CASH">Cash</option>
                                    <option value="OTHER">Other</option>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        required
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="e.g. Bitcoin"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Brokerage (Source)</label>
                                    <input
                                        type="text"
                                        name="brokerage"
                                        value={formData.brokerage}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="e.g. Binance"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Symbol (Opt)</label>
                                    <input
                                        type="text"
                                        name="symbol"
                                        value={formData.symbol}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="BTC"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                                    <input
                                        type="number"
                                        name="quantity"
                                        step="any"
                                        required
                                        value={formData.quantity}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Avg Buy Price</label>
                                    <input
                                        type="number"
                                        name="buy_price"
                                        step="any"
                                        required
                                        value={formData.buy_price}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Price</label>
                                    <input
                                        type="number"
                                        name="current_price"
                                        step="any"
                                        required
                                        value={formData.current_price}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
                                >
                                    Save Asset
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Assets;
