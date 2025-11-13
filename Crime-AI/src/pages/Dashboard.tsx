import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Upload as UploadIcon, 
  Shield, 
  AlertTriangle, 
  Users, 
  Clock,
  TrendingUp
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Videos Analyzed', value: '156', icon: Users, color: 'text-blue-600' },
    { label: 'Crimes Detected', value: '23', icon: AlertTriangle, color: 'text-red-600' },
    { label: 'Safety Alerts', value: '8', icon: Shield, color: 'text-green-600' },
    { label: 'Processing Time', value: '45s', icon: Clock, color: 'text-purple-600' },
  ];

  const features = [
    {
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning models analyze audio and visual content for criminal activity detection.',
      icon: TrendingUp,
      color: 'bg-blue-500',
    },
    {
      title: 'Real-time Processing',
      description: 'Upload videos and get instant crime analysis with safety recommendations.',
      icon: Clock,
      color: 'bg-green-500',
    },
    {
      title: 'Safety First',
      description: 'Immediate safety alerts and emergency procedures for witnesses.',
      icon: Shield,
      color: 'bg-red-500',
    },
    {
      title: 'Multi-modal Detection',
      description: 'Combines audio transcription, object detection, and behavioral analysis.',
      icon: Users,
      color: 'bg-purple-500',
    },
  ];

  const quickActions = [
    {
      title: 'Upload Video',
      description: 'Analyze a video for criminal activity',
      icon: UploadIcon,
      link: '/upload',
      color: 'bg-primary-600 hover:bg-primary-700',
    },
    {
      title: 'Safety Tips',
      description: 'Learn crime prevention strategies',
      icon: Shield,
      link: '#',
      color: 'bg-green-600 hover:bg-green-700',
    },
    {
      title: 'Emergency Contacts',
      description: 'Quick access to emergency numbers',
      icon: AlertTriangle,
      link: '#',
      color: 'bg-red-600 hover:bg-red-700',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Crime-AI Detection System
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Advanced AI-powered crime detection with real-time analysis and safety recommendations.
          Protect your community with intelligent surveillance technology.
        </p>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card">
              <div className="flex items-center space-x-3">
                <Icon className={`h-8 w-8 ${stat.color}`} />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                </div>
              </div>
            </div>
          );
        })}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Link
              key={index}
              to={action.link}
              className="card hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1"
            >
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-lg ${action.color} text-white`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </motion.div>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div key={index} className="card">
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${feature.color} text-white`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              </div>
            </div>
          );
        })}
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card bg-gradient-to-r from-primary-600 to-primary-700 text-white text-center"
      >
        <h2 className="text-2xl font-bold mb-4">Ready to Analyze?</h2>
        <p className="text-primary-100 mb-6">
          Upload a video file and get instant AI-powered crime detection analysis.
        </p>
        <Link
          to="/upload"
          className="btn-secondary bg-white text-primary-700 hover:bg-gray-100"
        >
          <UploadIcon className="h-5 w-5 mr-2" />
          Upload Video
        </Link>
      </motion.div>
    </div>
  );
};

export default Dashboard;
