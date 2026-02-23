import React, { useState, useEffect } from 'react';
import { UploadBox } from './components/UploadBox';
import { ResultsTable } from './components/ResultsTable';
import { DownloadButtons } from './components/DownloadButtons';
import { parseFiles, checkHealth } from './services/api';
import { Activity, CheckCircle, AlertTriangle, FileText } from 'lucide-react';

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [summary, setSummary] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking"); // checking, online, offline

  useEffect(() => {
    // Check backend health on mount
    checkHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  const handleFilesSelected = (newFiles) => {
    setFiles(prev => [...prev, ...newFiles]);
    // Reset results if new files added? Or append? 
    // Requirement says "Batch processing". Let's append to files list, but results are from a parse run.
    // If user adds files, they probably want to process them.
    // Let's keep it simple: Select files -> Process. 
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleClearAll = () => {
    setFiles([]);
    setResults([]);
    setSummary(null);
    setUploadProgress(0);
  };

  const handleProcess = async () => {
    if (files.length === 0) return;
    setIsProcessing(true);
    setUploadProgress(10); // Simulation start

    try {
      // Simulate progress for UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 5, 90));
      }, 500);

      const response = await parseFiles(files);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setResults(response.results);
      setSummary(response.summary);

    } catch (error) {
      alert("Processing failed. Ensure backend is running.");
    } finally {
      setIsProcessing(false);
      setTimeout(() => setUploadProgress(0), 1000); // Reset progress bar
    }
  };

  const handleUpdateResult = (rowIndex, fieldKey, newValue) => {
    setResults(prev => {
      const newResults = [...prev];
      // Update the specific field
      newResults[rowIndex].fields[fieldKey] = newValue;
      // Also update normalized if it exists, or just valid it's updated. 
      // The table displays what's in 'fields'.
      return newResults;
    });
  };

  return (
    <div className="min-h-screen p-8 font-sans text-gray-800 relative overflow-hidden bg-slate-900 bg-grid-pattern">
      {/* Decorative Document Outlines */}

      {/* Left Document Plaque */}
      <div
        className="pointer-events-none fixed top-[-5%] left-[-10%] w-[35rem] h-[45rem] document-outline animate-float opacity-70 flex flex-col p-10 space-y-6"
        style={{ '--rotation': '-8deg' }}
      >
        <div className="w-1/3 h-6 rounded bg-white/10"></div>
        <div className="w-full h-px bg-white/5"></div>
        <div className="w-3/4 h-4 rounded bg-white/5"></div>
        <div className="w-5/6 h-4 rounded bg-white/5"></div>
        <div className="w-2/3 h-4 rounded bg-white/5"></div>

        <div className="w-full h-32 rounded bg-white/5 mt-8 border border-white/10"></div>
      </div>

      {/* Right Document Plaque */}
      <div
        className="pointer-events-none fixed top-[15%] right-[-5%] w-[40rem] h-[55rem] document-outline animate-float animation-delay-2000 opacity-60 flex flex-col p-12 space-y-8"
        style={{ '--rotation': '6deg' }}
      >
        <div className="flex justify-between items-center w-full">
          <div className="w-1/4 h-8 rounded bg-white/10"></div>
          <div className="w-16 h-16 rounded-full bg-white/5"></div>
        </div>
        <div className="w-full h-px bg-white/5"></div>

        <div className="grid grid-cols-2 gap-6 w-full mt-4">
          <div className="h-10 rounded bg-white/5"></div>
          <div className="h-10 rounded bg-white/5"></div>
          <div className="h-10 rounded bg-white/5 col-span-2"></div>
        </div>

        <div className="w-full h-48 rounded bg-white/5 mt-8 border border-white/10 flex flex-col p-4 space-y-4 justify-center">
          <div className="w-full h-2 bg-white/10 rounded"></div>
          <div className="w-full h-2 bg-white/10 rounded"></div>
          <div className="w-3/4 h-2 bg-white/10 rounded"></div>
        </div>
      </div>

      {/* Bottom Floating Plaque */}
      <div
        className="pointer-events-none fixed bottom-[-15%] left-[25%] w-[45rem] h-[25rem] document-outline animate-float animation-delay-4000 opacity-40 flex flex-col p-8 space-y-6"
        style={{ '--rotation': '-2deg' }}
      >
        <div className="flex space-x-6 w-full">
          <div className="w-1/2 h-full flex flex-col space-y-4">
            <div className="w-1/2 h-4 rounded bg-white/10"></div>
            <div className="w-full h-3 rounded bg-white/5"></div>
            <div className="w-5/6 h-3 rounded bg-white/5"></div>
            <div className="w-4/5 h-3 rounded bg-white/5"></div>
          </div>
          <div className="w-1/2 h-full rounded border border-white/10 bg-white/5"></div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-8 relative z-10">

        {/* Header */}
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300 drop-shadow-sm">
              Offer Letter Extractor
            </h1>
            <p className="text-blue-100/70 mt-1 font-medium tracking-wide">Automated data extraction for HR teams</p>
          </div>
          <div className="flex items-center space-x-2 bg-slate-800/60 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-lg">
            <div className={`w-3 h-3 rounded-full ${backendStatus === 'online' ? 'bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.5)]' : 'bg-red-400 shadow-[0_0_10px_rgba(248,113,113,0.5)]'}`}></div>
            <span className="text-sm font-medium text-gray-200">
              System {backendStatus === 'online' ? 'Online' : 'Offline'}
            </span>
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Left Column: Upload & Actions */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/50">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-blue-500" />
                Input Files
              </h2>

              <UploadBox
                files={files}
                onFilesSelected={handleFilesSelected}
                onRemoveFile={handleRemoveFile}
                onClearAll={handleClearAll}
                isProcessing={isProcessing}
              />

              <div className="mt-6 flex flex-col space-y-3">
                {isProcessing && (
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                    <p className="text-center text-xs text-gray-500 mt-1">Processing... {uploadProgress}%</p>
                  </div>
                )}

                <button
                  onClick={handleProcess}
                  disabled={files.length === 0 || isProcessing}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 transition-all disabled:opacity-50 disabled:shadow-none"
                >
                  {isProcessing ? 'Extracting Data...' : `Process ${files.length} Files`}
                </button>
              </div>
            </div>

            {/* Summary Card */}
            {summary && (
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/50 animate-in fade-in slide-in-from-bottom-4">
                <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                  <Activity className="w-4 h-4 mr-2" /> Processing Summary
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 p-3 rounded-lg border border-green-100">
                    <div className="text-2xl font-bold text-green-600">{summary.success}</div>
                    <div className="text-xs text-green-700">Successful</div>
                  </div>
                  <div className="bg-red-50 p-3 rounded-lg border border-red-100">
                    <div className="text-2xl font-bold text-red-600">{summary.failed}</div>
                    <div className="text-xs text-red-700">Failed</div>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg border border-orange-100">
                    <div className="text-2xl font-bold text-orange-600">{summary.scanned_pdf}</div>
                    <div className="text-xs text-orange-700">Scanned PDFs</div>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-600">{summary.processing_seconds}s</div>
                    <div className="text-xs text-blue-700">Time Taken</div>
                  </div>
                </div>
              </div>
            )}

            {/* Export Actions */}
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/50">
              <h3 className="font-semibold text-gray-700 mb-3">Export Data</h3>
              <DownloadButtons results={results} disabled={isProcessing} />
            </div>
          </div>

          {/* Right Column: Results Table */}
          <div className="lg:col-span-8 h-[800px]">
            <ResultsTable
              results={results}
              onUpdateResult={handleUpdateResult}
            />
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;
