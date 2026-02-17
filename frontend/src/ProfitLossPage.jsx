import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PeriodReturnsChart from './PeriodReturnsChart';

export default function ProfitLossPage() {
    const navigate = useNavigate();

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex items-center gap-4 mb-6">
                <button
                    onClick={() => navigate('/')}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600"
                    aria-label="Back to Dashboard"
                >
                    <ArrowLeft size={24} />
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Portfolio Performance</h1>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <PeriodReturnsChart />
            </div>
        </div>
    );
}
