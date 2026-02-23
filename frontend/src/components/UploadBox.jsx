import React, { useCallback } from 'react';
// Manual drag and drop implementation used below
// Prompt said "Drag & drop". Using a lib is easier. 
// I didn't install react-dropzone. I should add it to the install list or implement manual drag/drop.
// Manual is safer to avoid extra deps if I forgot them. But react-dropzone is standard.
// I'll implement manual for now to match my installed deps (none yet). 
// Wait, I installed `framer-motion`, `lucide-react`.
// Let's use `lucide-react` for icons.

import { UploadCloud, File, X, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const UploadBox = ({ onFilesSelected, files, onRemoveFile, onClearAll, isProcessing }) => {
    const [isDragging, setIsDragging] = React.useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (isProcessing) return;

        const droppedFiles = Array.from(e.dataTransfer.files);
        validateAndAddFiles(droppedFiles);
    };

    const handleFileInput = (e) => {
        if (isProcessing) return;
        const selectedFiles = Array.from(e.target.files);
        validateAndAddFiles(selectedFiles);
    };

    const validateAndAddFiles = (newFiles) => {
        const validFiles = newFiles.filter(file => {
            const isDocx = file.name.toLowerCase().endsWith('.docx');
            const isPdf = file.name.toLowerCase().endsWith('.pdf');
            const isSizeValid = file.size <= 10 * 1024 * 1024; // 10MB
            return (isDocx || isPdf) && isSizeValid;
        });

        if (validFiles.length < newFiles.length) {
            alert("Some files were rejected. Only .docx/.pdf under 10MB allowed.");
        }

        onFilesSelected(validFiles);
    };

    return (
        <div className="w-full space-y-4">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={twMerge(
                    "border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-colors cursor-pointer bg-white/50 backdrop-blur-sm",
                    isDragging ? "border-blue-500 bg-blue-50/50" : "border-gray-300 hover:border-blue-400",
                    isProcessing && "opacity-50 cursor-not-allowed"
                )}
            >
                <input
                    type="file"
                    multiple
                    className="hidden"
                    id="fileInput"
                    onChange={handleFileInput}
                    disabled={isProcessing}
                    accept=".docx,.pdf"
                />
                <label htmlFor="fileInput" className="flex flex-col items-center cursor-pointer w-full h-full">
                    <UploadCloud className="w-12 h-12 text-blue-500 mb-4" />
                    <p className="text-lg font-medium text-gray-700">Drag & drop files here</p>
                    <p className="text-sm text-gray-500 mt-2">or click to browse (DOCX, PDF)</p>
                    <p className="text-xs text-gray-400 mt-4">Max 10MB per file</p>
                </label>
            </div>

            {files.length > 0 && (
                <div className="bg-white/70 backdrop-blur-md rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-semibold text-gray-700">Selected Files ({files.length})</h3>
                        <button
                            onClick={onClearAll}
                            disabled={isProcessing}
                            className="text-red-500 text-sm hover:underline disabled:opacity-50"
                        >
                            Clear All
                        </button>
                    </div>
                    <div className="max-h-60 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                        {files.map((file, index) => (
                            <div key={`${file.name}-${index}`} className="flex items-center justify-between p-2 bg-white rounded-lg border border-gray-100">
                                <div className="flex items-center space-x-3 overflow-hidden">
                                    <File className="w-4 h-4 text-gray-400 flex-shrink-0" />
                                    <span className="text-sm text-gray-600 truncate max-w-[200px]">{file.name}</span>
                                    <span className="text-xs text-gray-400">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                                </div>
                                {!isProcessing && (
                                    <button
                                        onClick={() => onRemoveFile(index)}
                                        className="text-gray-400 hover:text-red-500 transition-colors"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
