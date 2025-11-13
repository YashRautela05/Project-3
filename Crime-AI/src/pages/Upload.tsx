import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { 
  Upload as UploadIcon, 
  Video, 
  File, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  X
} from 'lucide-react';
import axios from 'axios';

interface UploadStatus {
  taskId: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
}

const Upload: React.FC = () => {
  const navigate = useNavigate();
  const [uploadStatus, setUploadStatus] = useState<UploadStatus | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    const maxSize = 100 * 1024 * 1024; // 100MB
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'audio/mp3', 'audio/wav'];

    // Validate file
    if (file.size > maxSize) {
      toast.error('File size must be less than 100MB');
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a valid video or audio file');
      return;
    }

    await handleFileUpload(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.aac', '.ogg']
    },
    multiple: false
  });

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadStatus({
      taskId: '',
      status: 'uploading',
      progress: 0,
      message: 'Uploading file...'
    });

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Upload file
      const uploadResponse = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setUploadStatus(prev => prev ? {
            ...prev,
            progress,
            message: `Uploading... ${progress}%`
          } : null);
        }
      });

      const { task_id } = uploadResponse.data;
      
      setUploadStatus({
        taskId: task_id,
        status: 'processing',
        progress: 100,
        message: 'Processing video...'
      });

      // Poll for status
      await pollTaskStatus(task_id);

    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed. Please try again.');
      setUploadStatus({
        taskId: '',
        status: 'error',
        progress: 0,
        message: 'Upload failed'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/status/${taskId}`);
        const { status, result } = response.data;

        if (status === 'SUCCESS') {
          setUploadStatus({
            taskId,
            status: 'completed',
            progress: 100,
            message: 'Analysis completed!'
          });
          toast.success('Analysis completed successfully!');
          
          // Navigate to results after a short delay
          setTimeout(() => {
            navigate(`/results/${taskId}`);
          }, 2000);
          
          return;
        } else if (status === 'FAILURE') {
          setUploadStatus({
            taskId,
            status: 'error',
            progress: 0,
            message: 'Analysis failed'
          });
          toast.error('Analysis failed. Please try again.');
          return;
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setUploadStatus({
            taskId,
            status: 'error',
            progress: 0,
            message: 'Analysis timed out'
          });
          toast.error('Analysis timed out. Please try again.');
        }
      } catch (error) {
        console.error('Status check error:', error);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000);
        }
      }
    };

    poll();
  };

  const getStatusIcon = () => {
    if (!uploadStatus) return null;
    
    switch (uploadStatus.status) {
      case 'uploading':
        return <UploadIcon className="h-6 w-6 text-blue-600 animate-pulse" />;
      case 'processing':
        return <Clock className="h-6 w-6 text-yellow-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'error':
        return <X className="h-6 w-6 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    if (!uploadStatus) return 'bg-gray-100';
    
    switch (uploadStatus.status) {
      case 'uploading':
        return 'bg-blue-100 border-blue-300';
      case 'processing':
        return 'bg-yellow-100 border-yellow-300';
      case 'completed':
        return 'bg-green-100 border-green-300';
      case 'error':
        return 'bg-red-100 border-red-300';
      default:
        return 'bg-gray-100';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Upload Video for Analysis</h1>
        <p className="text-gray-600">
          Upload a video or audio file to analyze for criminal activity using our AI-powered detection system.
        </p>
      </motion.div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="p-4 bg-primary-100 rounded-full">
                <Video className="h-8 w-8 text-primary-600" />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {isDragActive ? 'Drop your file here' : 'Drag & drop your file here'}
              </h3>
              <p className="text-gray-600 mb-4">
                or click to browse files
              </p>
            </div>

            <div className="text-sm text-gray-500 space-y-1">
              <p>Supported formats: MP4, AVI, MOV, MKV, MP3, WAV</p>
              <p>Maximum file size: 100MB</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Upload Status */}
      {uploadStatus && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`card border-2 ${getStatusColor()}`}
        >
          <div className="flex items-center space-x-4">
            {getStatusIcon()}
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{uploadStatus.message}</h3>
              {uploadStatus.status === 'uploading' && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadStatus.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              {uploadStatus.status === 'processing' && (
                <p className="text-sm text-gray-600 mt-1">
                  This may take 20-60 seconds depending on file size...
                </p>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Safety Notice */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card bg-yellow-50 border-yellow-200"
      >
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-6 w-6 text-yellow-600 mt-1" />
          <div>
            <h3 className="font-semibold text-yellow-800 mb-2">Important Safety Notice</h3>
            <p className="text-yellow-700 text-sm">
              If you witness a crime in progress, do not attempt to intervene. 
              Call 911 immediately and provide detailed information to law enforcement. 
              Your safety is the top priority.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Upload;
