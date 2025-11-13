import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  Shield, 
  CheckCircle, 
  XCircle, 
  HelpCircle,
  ArrowLeft,
  Download,
  Share2,
  Clock,
  Phone,
  Brain,
  Mic,
  Eye
} from 'lucide-react';
import axios from 'axios';

interface AnalysisResult {
  status: string;
  file_path: string;
  transcription: string;
  language: string;
  visual_summary: {
    detected_objects: string[];
  };
  video_caption: string;
  crime_analysis: {
    crime_analysis: string;
    status: string;
    method: string;
  };
  method: string;
}

const Results: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/status/${taskId}`);
      const { status, result: analysisResult } = response.data;

      if (status === 'SUCCESS') {
        setResult(analysisResult);
      } else if (status === 'FAILURE') {
        setError('Analysis failed. Please try again.');
      } else {
        setError('Analysis is still in progress...');
      }
    } catch (error) {
      console.error('Error fetching results:', error);
      setError('Failed to load analysis results.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (taskId) {
      fetchResults();
    }
  }, [taskId, fetchResults]);

  const getCrimeStatus = () => {
    if (!result?.crime_analysis?.crime_analysis) return 'unknown';
    
    const analysis = result.crime_analysis.crime_analysis.toLowerCase();
    if (analysis.includes('criminal activity detected: yes')) return 'detected';
    if (analysis.includes('criminal activity detected: no')) return 'safe';
    return 'unknown';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'detected':
        return 'text-red-600 bg-red-100 border-red-300';
      case 'safe':
        return 'text-green-600 bg-green-100 border-green-300';
      default:
        return 'text-yellow-600 bg-yellow-100 border-yellow-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'detected':
        return <AlertTriangle className="h-6 w-6" />;
      case 'safe':
        return <CheckCircle className="h-6 w-6" />;
      default:
        return <Shield className="h-6 w-6" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <Clock className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center">
        <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <Link to="/upload" className="btn-primary">
          Try Again
        </Link>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center">
        <p className="text-gray-600">No results found.</p>
      </div>
    );
  }

  const crimeStatus = getCrimeStatus();

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Analysis Results</h1>
        <p className="text-gray-600">
          AI-powered crime detection analysis completed
        </p>
      </motion.div>

      {/* Crime Status Alert */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className={`card border-2 ${getStatusColor(crimeStatus)}`}
      >
        <div className="flex items-center space-x-4">
          {getStatusIcon(crimeStatus)}
          <div>
            <h2 className="text-xl font-semibold">
              {crimeStatus === 'detected' ? 'Criminal Activity Detected' : 
               crimeStatus === 'safe' ? 'No Criminal Activity Detected' : 
               'Analysis Complete'}
            </h2>
            <p className="text-sm opacity-80">
              {crimeStatus === 'detected' ? 'Immediate action recommended' :
               crimeStatus === 'safe' ? 'No immediate safety concerns' :
               'Review analysis details below'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Emergency Actions */}
      {crimeStatus === 'detected' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-red-50 border-red-200"
        >
          <div className="flex items-start space-x-4">
            <Phone className="h-6 w-6 text-red-600 mt-1" />
            <div>
              <h3 className="font-semibold text-red-800 mb-2">Emergency Actions Required</h3>
              <div className="space-y-2 text-sm text-red-700">
                <p>• Call 911 immediately if crime is in progress</p>
                <p>• Do not approach or confront anyone involved</p>
                <p>• Document details for law enforcement</p>
                <p>• Stay at a safe distance</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Analysis Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold">AI Analysis</h3>
          </div>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto">
              {result.crime_analysis?.crime_analysis || 'No analysis available'}
            </pre>
          </div>
        </motion.div>

        {/* Technical Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          {/* Audio Analysis */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <Mic className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-semibold">Audio Analysis</h3>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Language:</span> {result.language || 'Not detected'}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Transcription:</span>
              </p>
              <p className="text-sm bg-gray-50 p-3 rounded">
                {result.transcription || 'No audio content detected'}
              </p>
            </div>
          </div>

          {/* Visual Analysis */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <Eye className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold">Visual Analysis</h3>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Detected Objects:</span>
              </p>
              <div className="flex flex-wrap gap-2">
                {result.visual_summary?.detected_objects?.map((obj, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                    {obj}
                  </span>
                )) || <span className="text-gray-500">None detected</span>}
              </div>
              <p className="text-sm text-gray-600 mt-3">
                <span className="font-medium">Video Caption:</span>
              </p>
              <p className="text-sm bg-gray-50 p-3 rounded">
                {result.video_caption || 'No caption available'}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="flex flex-wrap gap-4 justify-center"
      >
        <Link to="/upload" className="btn-primary">
          Analyze Another Video
        </Link>
        <button className="btn-secondary">
          <Download className="h-4 w-4 mr-2" />
          Download Report
        </button>
        <button className="btn-secondary">
          <Share2 className="h-4 w-4 mr-2" />
          Share Results
        </button>
      </motion.div>
    </div>
  );
};

export default Results;
