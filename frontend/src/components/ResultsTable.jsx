import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Edit2, Save, X, Download } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const CONFIDENCE_THRESHOLD = 0.8;

const TableCell = ({ value, confidence, onSave, isEditing, setIsEditing, fieldKey }) => {
    const [localValue, setLocalValue] = useState(value);

    useEffect(() => {
        setLocalValue(value);
    }, [value]);

    const handleSave = () => {
        onSave(fieldKey, localValue);
        setIsEditing(null);
    };

    const handleCancel = () => {
        setLocalValue(value);
        setIsEditing(null);
    };

    if (isEditing === fieldKey) {
        return (
            <div className="flex items-center space-x-2">
                <input
                    type="text"
                    value={localValue || ''}
                    onChange={(e) => setLocalValue(e.target.value)}
                    className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                    autoFocus
                />
                <button onClick={handleSave} className="text-green-600 hover:text-green-800"><Save className="w-4 h-4" /></button>
                <button onClick={handleCancel} className="text-red-600 hover:text-red-800"><X className="w-4 h-4" /></button>
            </div>
        );
    }

    return (
        <div className="flex items-center justify-between group">
            <span className={clsx(
                "truncate block max-w-[150px]",
                !value && "text-gray-400 italic"
            )}>
                {value || "Missing"}
            </span>
            {confidence < CONFIDENCE_THRESHOLD && (
                <AlertCircle className="w-3 h-3 text-orange-500 ml-1 flex-shrink-0" title={`Low Confidence: ${(confidence * 100).toFixed(0)}%`} />
            )}
            <button
                onClick={() => setIsEditing(fieldKey)}
                className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 text-gray-400 hover:text-blue-500"
            >
                <Edit2 className="w-3 h-3" />
            </button>
        </div>
    );
};

export const ResultsTable = ({ results, onUpdateResult }) => {
    const [editingRow, setEditingRow] = useState(null); // { rowIndex, fieldKey }
    const [filterLowConfidence, setFilterLowConfidence] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    // Fields to display
    const columns = [
        { key: 'designation', label: 'Designation' },
        { key: 'location_city', label: 'City' },
        { key: 'location_state', label: 'State' },
        { key: 'date_of_joining_norm', label: 'Joining Date' },
        { key: 'date_of_joining_raw', label: 'Joining Date (Raw)' },
        { key: 'comp_total_annual_inr', label: 'Total CTC' },
        { key: 'comp_total_annual_raw', label: 'Total CTC (Raw)' },
        { key: 'byod_clause', label: 'BYOD' },
        { key: 'scheduleA_competency', label: 'Competency' },
        { key: 'scheduleA_band', label: 'Band' },
        { key: 'scheduleA_grade', label: 'Grade' },
        { key: 'gross_salary', label: 'Gross Salary' },
        { key: 'long_term_benefits', label: 'Long Term Benefits' },
        { key: 'fixed_ctc', label: 'Fixed CTC' },
        { key: 'total_ctc', label: 'Table Total CTC' }
    ];

    const filteredResults = results.filter(row => {
        // 1. Search Filter
        const matchesSearch = Object.values(row.fields).some(val =>
            String(val).toLowerCase().includes(searchTerm.toLowerCase())
        ) || row.file_name.toLowerCase().includes(searchTerm.toLowerCase());

        // 2. Low Confidence Filter
        const hasLowConfidence = Object.values(row.confidence).some(conf => conf < CONFIDENCE_THRESHOLD);

        if (filterLowConfidence && !hasLowConfidence) return false;

        return matchesSearch;
    });

    const handleCellSave = (rowIndex, fieldKey, newValue) => {
        onUpdateResult(rowIndex, fieldKey, newValue);
    };

    return (
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 overflow-hidden flex flex-col h-full">
            {/* Toolbar */}
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                <div className="flex items-center space-x-4">
                    <h2 className="text-lg font-bold text-gray-800">Extraction Results</h2>
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">{results.length} Files</span>
                </div>

                <div className="flex items-center space-x-3">
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    />

                    <label className="flex items-center space-x-2 text-sm text-gray-600 cursor-pointer select-none">
                        <input
                            type="checkbox"
                            checked={filterLowConfidence}
                            onChange={(e) => setFilterLowConfidence(e.target.checked)}
                            className="rounded text-blue-500 focus:ring-blue-500"
                        />
                        <span>Show Cleanup Needed</span>
                    </label>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-auto flex-1 custom-scrollbar">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-gray-50 sticky top-0 z-10 shadow-sm">
                        <tr>
                            <th className="p-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-40">File Name</th>
                            {columns.map(col => (
                                <th key={col.key} className="p-4 text-xs font-semibold text-gray-500 uppercase tracking-wider min-w-[140px]">
                                    {col.label}
                                </th>
                            ))}
                            <th className="p-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-20">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {filteredResults.map((row, rowIndex) => (
                            <React.Fragment key={rowIndex}>
                                <tr className="hover:bg-blue-50/30 transition-colors">
                                    {/* File Name */}
                                    <td className="p-4 text-sm font-medium text-gray-700 bg-white/50 sticky left-0 z-10">
                                        <div className="flex items-center space-x-2" title={row.file_name}>
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-400"></div>
                                            <span className="truncate max-w-[120px]">{row.file_name}</span>
                                        </div>
                                        {row.error_code && (
                                            <div className="text-xs text-red-500 mt-1">{row.error_code}</div>
                                        )}
                                    </td>

                                    {/* Data Columns */}
                                    {columns.map(col => {
                                        const tableKeys = ['gross_salary', 'long_term_benefits', 'fixed_ctc', 'total_ctc'];

                                        let value = null;
                                        let confidence = 0;

                                        if (tableKeys.includes(col.key)) {
                                            value = row.fields.salary_table_totals?.[col.key];
                                            confidence = row.confidence['salary_table_totals'] || 0;
                                        } else {
                                            value = row.fields[col.key];
                                            confidence = row.confidence[col.key] || 0;
                                        }

                                        return (
                                            <td key={col.key} className={clsx(
                                                "p-4 text-sm border-l border-transparent hover:border-gray-200 transition-colors",
                                                confidence < CONFIDENCE_THRESHOLD ? "bg-orange-50/50" : ""
                                            )}>
                                                <TableCell
                                                    value={value}
                                                    confidence={confidence}
                                                    fieldKey={col.key}
                                                    isEditing={editingRow?.rowIndex === rowIndex && editingRow?.fieldKey === col.key ? col.key : null}
                                                    setIsEditing={(key) => setEditingRow(key ? { rowIndex, fieldKey: key } : null)}
                                                    onSave={(key, val) => handleCellSave(rowIndex, key, val)}
                                                />
                                            </td>
                                        );
                                    })}

                                    {/* Status Column */}
                                    <td className="p-4">
                                        <div className="flex items-center space-x-2">
                                            {row.error_code ? (
                                                <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-1 rounded-full">Error</span>
                                            ) : (
                                                <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-1 rounded-full">Success</span>
                                            )}
                                            <button
                                                onClick={() => setEditingRow(editingRow?.expandedRow === rowIndex ? null : { expandedRow: rowIndex })}
                                                className="text-xs text-blue-600 hover:text-blue-800 underline ml-2 whitespace-nowrap"
                                            >
                                                {editingRow?.expandedRow === rowIndex ? 'Hide Details' : 'View Computed Rows'}
                                            </button>
                                        </div>
                                    </td>
                                </tr>

                                {/* Expanded Salary Table Details */}
                                {editingRow?.expandedRow === rowIndex && (
                                    <tr className="bg-gray-50/80">
                                        <td colSpan={columns.length + 2} className="p-4 border-t border-gray-100">
                                            <div className="ml-8 border-l-2 border-blue-400 pl-4 py-2">
                                                <h4 className="text-sm font-semibold text-gray-700 mb-2">Detailed Salary Components:</h4>
                                                {row.fields.salary_table_rows && row.fields.salary_table_rows.length > 0 ? (
                                                    <div className="overflow-x-auto">
                                                        <table className="min-w-full text-sm text-left">
                                                            <thead className="text-xs text-gray-500 uppercase bg-white">
                                                                <tr>
                                                                    <th className="px-4 py-2 font-medium">Component</th>
                                                                    <th className="px-4 py-2 font-medium text-right">Per Annum (INR)</th>
                                                                    <th className="px-4 py-2 font-medium text-right">Per Month (INR)</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-gray-200">
                                                                {row.fields.salary_table_rows.map((r, i) => (
                                                                    <tr key={i} className="bg-white">
                                                                        <td className="px-4 py-2 font-medium text-gray-800">{r.component}</td>
                                                                        <td className="px-4 py-2 text-right">{r.per_annum?.toLocaleString()}</td>
                                                                        <td className="px-4 py-2 text-right">{r.per_month?.toLocaleString()}</td>
                                                                    </tr>
                                                                ))}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                ) : (
                                                    <p className="text-sm text-gray-500 italic">No salary rows detected for this file.</p>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>

                {filteredResults.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-40 text-gray-400">
                        <p>No results found matching your filters.</p>
                    </div>
                )}
            </div>
        </div>
    );
};
