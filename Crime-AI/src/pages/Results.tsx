import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft,
  Loader2,
  AlertTriangle
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import ResultsDisplay from '../components/ResultsDisplay';

interface AnalysisResult {
  task_id: string;
  status: string;
  result: any;
}

const Results: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!taskId) {
        setError('No task ID provided');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/status/${taskId}`);
        console.log('API Response:', response.data);
        
        if (response.data.status === 'done') {
          console.log('Analysis complete, setting result:', response.data);
          setAnalysisResult(response.data);
          setLoading(false);
        } else if (response.data.status === 'FAILURE') {
          setError('Analysis failed. Please try again.');
          setLoading(false);
          toast.error('Analysis failed');
        } else {
          // Still processing, poll again
          setTimeout(fetchResults, 3000);
        }
      } catch (err) {
        console.error('Error fetching results:', err);
        setError('Failed to load results. Please try again.');
        setLoading(false);
        toast.error('Failed to load results');
      }
    };

    fetchResults();
  }, [taskId]);

  const handleBackToUpload = () => {
    navigate('/upload');
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="h-12 w-12 text-primary-600 animate-spin" />
        <h2 className="text-2xl font-semibold text-gray-900">Loading Analysis Results...</h2>
        <p className="text-gray-600">Please wait while we fetch your analysis data.</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-red-50 border-2 border-red-300"
        >
          <AlertTriangle className="h-16 w-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-900 mb-2">Error Loading Results</h2>
          <p className="text-red-700 mb-6">{error}</p>
          <button
            onClick={handleBackToUpload}
            className="btn-primary flex items-center space-x-2 mx-auto"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Upload</span>
          </button>
        </motion.div>
      </div>
    );
  }

  // Results display
  if (analysisResult && analysisResult.status === 'done') {
    return (
      <div className="space-y-6">
        {/* Header with back button */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <button
            onClick={handleBackToUpload}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>New Analysis</span>
          </button>
        </motion.div>

        {/* Results Display Component */}
        <ResultsDisplay data={analysisResult} />
      </div>
    );
  }

  // Fallback
  return (
    <div className="text-center">
      <p className="text-gray-600">No results available.</p>
      <button
        onClick={handleBackToUpload}
        className="btn-primary mt-4"
      >
        Back to Upload
      </button>
    </div>
  );
};

export default Results;