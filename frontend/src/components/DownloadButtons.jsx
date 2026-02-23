import React from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import { exportCSV, exportXLSX } from '../services/api';

export const DownloadButtons = ({ results, disabled }) => {
    const handleDownloadCSV = async () => {
        if (disabled || results.length === 0) return;
        try {
            await exportCSV({ results });
        } catch (e) {
            alert("Export failed");
        }
    };

    const handleDownloadXLSX = async () => {
        if (disabled || results.length === 0) return;
        try {
            await exportXLSX({ results });
        } catch (e) {
            alert("Export failed");
        }
    };

    return (
        <div className="flex space-x-3">
            <button
                onClick={handleDownloadCSV}
                disabled={disabled || results.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Download className="w-4 h-4" />
                <span>Export CSV</span>
            </button>

            <button
                onClick={handleDownloadXLSX}
                disabled={disabled || results.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <FileSpreadsheet className="w-4 h-4" />
                <span>Export Excel</span>
            </button>
        </div>
    );
};
