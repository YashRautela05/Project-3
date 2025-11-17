import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Shield,
  Activity,
  Users,
  Eye,
  TrendingUp,
  Clock,
  MapPin,
  ChevronDown,
  ChevronUp,
  FileText,
  Target,
  Zap,
  CheckCircle,
  XCircle,
  Info,
  AlertOctagon,
  Phone
} from 'lucide-react';

interface ResultsDisplayProps {
  data: any;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ data }) => {
  console.log('ResultsDisplay received data:', data);
  console.log('Data has result?', !!data?.result);
  console.log('Result has summary?', !!data?.result?.summary);
  console.log('Result has crime_report?', !!data?.result?.crime_report);
  
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    summary: true,
    crimeReport: true,
    detections: false,
    actions: false,
    motion: false,
    events: false,
    gemini: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'text-red-600 bg-red-100 border-red-300';
      case 'high':
        return 'text-orange-600 bg-orange-100 border-orange-300';
      case 'medium':
      case 'moderate':
        return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'low':
        return 'text-green-600 bg-green-100 border-green-300';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertOctagon className="h-6 w-6" />;
      case 'medium':
      case 'moderate':
        return <AlertTriangle className="h-6 w-6" />;
      case 'low':
        return <Info className="h-6 w-6" />;
      default:
        return <Shield className="h-6 w-6" />;
    }
  };

  // Add null checking
  if (!data || !data.result) {
    return (
      <div className="max-w-2xl mx-auto text-center p-8 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
        <AlertTriangle className="h-12 w-12 text-yellow-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-yellow-900 mb-2">Invalid Data</h3>
        <p className="text-yellow-700">The analysis data is incomplete or invalid.</p>
      </div>
    );
  }

  const result = data.result;
  const summary = result.summary || {};
  const crimeReport = result.crime_report || result.crime_analysis || {};
  const geminiOutput = result.gemini_output || {};

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Alert */}
      {crimeReport && crimeReport.overall_severity && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`card border-2 ${getSeverityColor(crimeReport.overall_severity)}`}
        >
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              {getSeverityIcon(crimeReport.overall_severity)}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-2xl font-bold uppercase">
                  {crimeReport.overall_severity} SEVERITY
                </h2>
                <div className="flex items-center space-x-2">
                  {crimeReport.crime_detected ? (
                    <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm font-semibold">
                      CRIME DETECTED
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-semibold">
                      NO CRIME DETECTED
                    </span>
                  )}
                </div>
              </div>
              {crimeReport.recommendation && (
                <p className="text-lg font-medium mb-3">{crimeReport.recommendation}</p>
              )}
              
              {/* Crime Indicators */}
              {crimeReport.crime_indicators && crimeReport.crime_indicators.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {crimeReport.crime_indicators.map((indicator: any, idx: number) => (
                    <span
                      key={idx}
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(indicator.severity)}`}
                    >
                      {indicator.type.replace(/_/g, ' ').toUpperCase()} ({Math.round(indicator.confidence * 100)}%)
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Gemini AI Analysis */}
      {geminiOutput && geminiOutput.description && (
        <CollapsibleSection
          title="AI Analysis Summary"
          icon={<Zap className="h-5 w-5" />}
          isExpanded={expandedSections.gemini}
          onToggle={() => toggleSection('gemini')}
        >
          <div className="space-y-4">
            <p className="text-gray-700 leading-relaxed">{geminiOutput.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Crime Type</h4>
                <p className="text-gray-700 capitalize">{geminiOutput.crime_type?.replace(/_/g, ' ') || 'N/A'}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Severity</h4>
                <p className={`font-bold uppercase ${getSeverityColor(geminiOutput.severity)}`}>
                  {geminiOutput.severity}
                </p>
              </div>
            </div>

            {geminiOutput.evidence_summary && geminiOutput.evidence_summary.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <FileText className="h-4 w-4 mr-2" />
                  Evidence Summary
                </h4>
                <ul className="space-y-2">
                  {geminiOutput.evidence_summary.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {geminiOutput.safety_recommendations && geminiOutput.safety_recommendations.length > 0 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  Safety Recommendations
                </h4>
                <ul className="space-y-2">
                  {geminiOutput.safety_recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <span className="text-red-900 font-medium">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {geminiOutput.legal_information?.ipc_sections && geminiOutput.legal_information.ipc_sections.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Legal Information (IPC Sections)</h4>
                <div className="space-y-2">
                  {geminiOutput.legal_information.ipc_sections.map((ipc: any, idx: number) => (
                    <div key={idx} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="font-semibold text-blue-900">{ipc.section}</div>
                      <div className="text-sm text-blue-700 mb-1"><strong>Offense:</strong> {ipc.offense}</div>
                      <div className="text-sm text-blue-600"><strong>Punishment:</strong> {ipc.punishment}</div>
                    </div>
                  ))}
                </div>
                {geminiOutput.legal_information.possible_punishment && (
                  <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <h5 className="font-semibold text-amber-900 mb-1">Possible Punishment</h5>
                    <p className="text-sm text-amber-800">{geminiOutput.legal_information.possible_punishment}</p>
                  </div>
                )}
              </div>
            )}
            
            {geminiOutput.how_to_stay_safe && geminiOutput.how_to_stay_safe.length > 0 && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <Shield className="h-4 w-4 mr-2" />
                  How to Stay Safe
                </h4>
                <ul className="space-y-2">
                  {geminiOutput.how_to_stay_safe.map((tip: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span className="text-blue-900">{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {geminiOutput.immediate_actions && geminiOutput.immediate_actions.length > 0 && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                  <AlertOctagon className="h-4 w-4 mr-2" />
                  Immediate Actions Required
                </h4>
                <ul className="space-y-2">
                  {geminiOutput.immediate_actions.map((action: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <AlertTriangle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                      <span className="text-orange-900 font-medium">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {geminiOutput.disclaimer && (
              <div className="p-3 bg-gray-100 border border-gray-300 rounded-lg">
                <p className="text-xs text-gray-600 italic">{geminiOutput.disclaimer}</p>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Quick Stats */}
      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          <StatCard
            label="Frames Analyzed"
            value={summary.frames_analyzed || 0}
            icon={<Eye className="h-5 w-5" />}
            color="text-blue-600 bg-blue-100"
          />
          <StatCard
            label="Unique Objects"
            value={summary.detections_summary?.unique_objects?.length || 0}
            icon={<Target className="h-5 w-5" />}
            color="text-purple-600 bg-purple-100"
          />
          <StatCard
            label="Events Detected"
            value={result.events?.length || 0}
            icon={<Activity className="h-5 w-5" />}
            color="text-orange-600 bg-orange-100"
          />
          <StatCard
            label="FPS"
            value={summary.frames_per_second || 0}
            icon={<Clock className="h-5 w-5" />}
            color="text-green-600 bg-green-100"
          />
        </motion.div>
      )}

      {/* Detailed Crime Analysis */}
      <CollapsibleSection
        title="Detailed Crime Analysis"
        icon={<Shield className="h-5 w-5" />}
        isExpanded={expandedSections.crimeReport}
        onToggle={() => toggleSection('crimeReport')}
      >
        <div className="space-y-6">
          {/* Weapon Threat Analysis */}
          {crimeReport.weapon_threat_analysis?.detected && (
            <AnalysisCard
              title="Weapon Threat Analysis"
              severity={crimeReport.weapon_threat_analysis.threat_level}
              assessment={crimeReport.weapon_threat_analysis.assessment}
            >
              <div className="space-y-4">
                {crimeReport.weapon_threat_analysis.weapon_frames?.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 mb-2">Weapon Detections:</h5>
                    <div className="space-y-2">
                      {crimeReport.weapon_threat_analysis.weapon_frames.map((frame: any, idx: number) => (
                        <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-medium">Frame {frame.frame_index}: {frame.frame_name}</span>
                            <span className="text-sm text-gray-600">
                              {frame.weapon_count} weapon(s), {frame.person_count} person(s)
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {frame.weapons.map((weapon: any, wIdx: number) => (
                              <span key={wIdx} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                                {weapon.type} ({Math.round(weapon.confidence * 100)}%)
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {crimeReport.weapon_threat_analysis.proximity_alerts?.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 mb-2">Proximity Alerts:</h5>
                    <div className="space-y-2">
                      {crimeReport.weapon_threat_analysis.proximity_alerts.map((alert: any, idx: number) => (
                        <div key={idx} className="p-2 bg-yellow-50 border border-yellow-300 rounded">
                          <span className="text-sm">
                            Frame {alert.frame_index}: {alert.weapon_type} within {Math.round(alert.distance)}px of person
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </AnalysisCard>
          )}

          {/* Violence Analysis */}
          {crimeReport.violence_analysis?.detected && (
            <AnalysisCard
              title="Violence Analysis"
              severity={crimeReport.violence_analysis.intensity_level}
              assessment={crimeReport.violence_analysis.assessment}
            >
              <div className="space-y-3">
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <div className="text-sm text-gray-600 mb-1">Violence Score</div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-red-600 h-3 rounded-full transition-all"
                        style={{ width: `${crimeReport.violence_analysis.violence_score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-red-600">
                    {Math.round(crimeReport.violence_analysis.violence_score * 100)}%
                  </div>
                </div>

                {crimeReport.violence_analysis.violent_actions?.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 mb-2">Violent Actions Detected:</h5>
                    <div className="space-y-2">
                      {crimeReport.violence_analysis.violent_actions.map((action: any, idx: number) => (
                        <div key={idx} className="p-2 bg-orange-50 border border-orange-200 rounded">
                          <div className="flex justify-between">
                            <span className="font-medium">{action.action}</span>
                            <span className="text-sm">Confidence: {Math.round(action.confidence * 100)}%</span>
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            Intensity: {Math.round(action.intensity * 100)}% | Clip: {action.clip_index}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </AnalysisCard>
          )}

          {/* Theft Analysis */}
          <AnalysisCard
            title="Theft Analysis"
            severity={crimeReport.theft_analysis.detected ? 'high' : 'low'}
            assessment={crimeReport.theft_analysis.assessment}
          >
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Theft Probability:</span>
                <span className="font-semibold">{Math.round(crimeReport.theft_analysis.theft_probability * 100)}%</span>
              </div>
              {crimeReport.theft_analysis.valuable_disappearances?.length > 0 && (
                <div>
                  <h5 className="font-semibold text-gray-900 mb-2">Items Disappeared:</h5>
                  <div className="space-y-1">
                    {crimeReport.theft_analysis.valuable_disappearances.map((item: any, idx: number) => (
                      <div key={idx} className="text-sm text-gray-700">• {item}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </AnalysisCard>

          {/* Suspicious Behavior */}
          {crimeReport.suspicious_behavior_analysis?.detected && (
            <AnalysisCard
              title="Suspicious Behavior Analysis"
              severity="medium"
              assessment={crimeReport.suspicious_behavior_analysis.assessment}
            >
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Suspicion Score:</span>
                  <span className="font-semibold">{Math.round(crimeReport.suspicious_behavior_analysis.suspicion_score * 100)}%</span>
                </div>
                
                {crimeReport.suspicious_behavior_analysis.patterns?.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 mb-2">Patterns Detected:</h5>
                    <div className="space-y-2">
                      {crimeReport.suspicious_behavior_analysis.patterns.map((pattern: any, idx: number) => (
                        <div key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                          <div className="flex justify-between mb-1">
                            <span className="font-medium capitalize">{pattern.type.replace(/_/g, ' ')}</span>
                            <span className="text-sm">Confidence: {Math.round(pattern.confidence * 100)}%</span>
                          </div>
                          <p className="text-sm text-gray-700">{pattern.details}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </AnalysisCard>
          )}
        </div>
      </CollapsibleSection>

      {/* Object Detection Summary */}
      <CollapsibleSection
        title="Object Detection Summary"
        icon={<Eye className="h-5 w-5" />}
        isExpanded={expandedSections.detections}
        onToggle={() => toggleSection('detections')}
      >
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Unique Objects Detected:</h4>
            <div className="flex flex-wrap gap-2">
              {summary.detections_summary.unique_objects.map((obj: string, idx: number) => (
                <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {obj}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Sample Detections (First 4 Frames):</h4>
            <div className="space-y-3">
              {summary.detections_summary.sample_detections.slice(0, 4).map((detection: any, idx: number) => (
                <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium">{detection.frame} (Frame {detection.frame_index})</span>
                    <span className="text-sm text-gray-600">{detection.objects.length} objects</span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {detection.objects.map((obj: any, oIdx: number) => (
                      <div key={oIdx} className="p-2 bg-white border rounded text-sm">
                        <div className="font-medium">{obj.label}</div>
                        <div className="text-xs text-gray-600">{Math.round(obj.conf * 100)}% confidence</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Motion Analysis */}
      {summary.motion_analysis?.analyzed && (
        <CollapsibleSection
          title="Motion Analysis"
          icon={<Activity className="h-5 w-5" />}
          isExpanded={expandedSections.motion}
          onToggle={() => toggleSection('motion')}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Average Motion</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.motion_analysis.average_motion.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Max Motion</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.motion_analysis.max_motion.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Motion Variance</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.motion_analysis.motion_variance.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h5 className="font-semibold text-blue-900 mb-2">Motion Pattern</h5>
            <div className="space-y-1">
              <div className="text-sm">
                <span className="text-gray-700">Category: </span>
                <span className="font-medium capitalize">{summary.motion_analysis.motion_pattern.category.replace(/_/g, ' ')}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-700">Description: </span>
                <span>{summary.motion_analysis.motion_pattern.description}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-700">Crime Relevance: </span>
                <span className={`font-medium ${
                  summary.motion_analysis.motion_pattern.crime_relevance === 'high' ? 'text-red-600' :
                  summary.motion_analysis.motion_pattern.crime_relevance === 'medium' ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {summary.motion_analysis.motion_pattern.crime_relevance.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* Action Recognition */}
      {summary.actions_summary?.clips?.length > 0 && (
        <CollapsibleSection
          title="Action Recognition"
          icon={<TrendingUp className="h-5 w-5" />}
          isExpanded={expandedSections.actions}
          onToggle={() => toggleSection('actions')}
        >
          <div className="space-y-4">
            {summary.actions_summary.clips.map((clip: any, idx: number) => (
              <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h5 className="font-semibold text-gray-900">Clip {clip.clip_index}</h5>
                    <p className="text-sm text-gray-600">
                      Frames {clip.frame_range.start} - {clip.frame_range.end} ({clip.num_frames_analyzed} frames)
                    </p>
                  </div>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm capitalize">
                    {clip.clip_type}
                  </span>
                </div>

                <h6 className="font-semibold text-gray-900 mb-2">Top Actions Detected:</h6>
                <div className="space-y-2">
                  {clip.top_actions.slice(0, 10).map((action: any, aIdx: number) => (
                    <div
                      key={aIdx}
                      className={`p-3 rounded-lg border ${
                        action.is_crime_relevant
                          ? 'bg-red-50 border-red-300'
                          : 'bg-white border-gray-200'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <span className={`font-medium ${action.is_crime_relevant ? 'text-red-900' : 'text-gray-900'}`}>
                            {aIdx + 1}. {action.label}
                          </span>
                          {action.is_crime_relevant && (
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                          )}
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                action.is_crime_relevant ? 'bg-red-600' : 'bg-blue-600'
                              }`}
                              style={{ width: `${action.prob * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium w-12 text-right">
                            {Math.round(action.prob * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Events Timeline */}
      <CollapsibleSection
        title={`Events Timeline (${result.events.length} events)`}
        icon={<MapPin className="h-5 w-5" />}
        isExpanded={expandedSections.events}
        onToggle={() => toggleSection('events')}
      >
        <div className="space-y-2">
          {result.events.map((event: any, idx: number) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border ${getSeverityColor(event.severity)}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  {event.severity === 'high' && <AlertOctagon className="h-4 w-4" />}
                  {event.severity === 'medium' && <AlertTriangle className="h-4 w-4" />}
                  {event.severity === 'low' && <Info className="h-4 w-4" />}
                  <span className="font-medium capitalize">{event.type.replace(/_/g, ' ')}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{event.severity.toUpperCase()}</div>
                  <div className="text-xs">{Math.round(event.confidence * 100)}% confidence</div>
                </div>
              </div>
              
              {event.frame && (
                <div className="text-sm text-gray-700 mb-1">
                  Frame: {event.frame} (Index: {event.frame_index})
                </div>
              )}
              
              {event.details && (
                <div className="text-sm text-gray-600 mt-2">
                  {Object.entries(event.details).map(([key, value]: [string, any]) => (
                    <div key={key}>
                      <span className="font-medium">{key.replace(/_/g, ' ')}: </span>
                      <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* Metadata */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="card bg-gray-50"
      >
        <h3 className="font-semibold text-gray-900 mb-3">Analysis Metadata</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Task ID</div>
            <div className="font-mono text-xs break-all">{data.task_id}</div>
          </div>
          <div>
            <div className="text-gray-600">Video Hash</div>
            <div className="font-mono text-xs break-all">{summary.video_hash.substring(0, 16)}...</div>
          </div>
          <div>
            <div className="text-gray-600">Analysis Version</div>
            <div className="font-medium">{result.metadata.analysis_version}</div>
          </div>
          <div>
            <div className="text-gray-600">Models Used</div>
            <div className="text-xs">{result.metadata.models_used.join(', ')}</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// Helper Components
interface CollapsibleSectionProps {
  title: string;
  icon: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  icon,
  isExpanded,
  onToggle,
  children
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between mb-4 hover:text-primary-600 transition-colors"
      >
        <div className="flex items-center space-x-2">
          {icon}
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-500" />
        )}
      </button>
      
      {isExpanded && <div className="mt-4">{children}</div>}
    </motion.div>
  );
};

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color }) => {
  return (
    <div className="card">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${color}`}>
          {icon}
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          <div className="text-sm text-gray-600">{label}</div>
        </div>
      </div>
    </div>
  );
};

interface AnalysisCardProps {
  title: string;
  severity: string;
  assessment: string;
  children: React.ReactNode;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({ title, severity, assessment, children }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'border-red-300 bg-red-50';
      case 'high':
        return 'border-orange-300 bg-orange-50';
      case 'medium':
      case 'moderate':
        return 'border-yellow-300 bg-yellow-50';
      case 'low':
        return 'border-green-300 bg-green-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className={`p-4 border-2 rounded-lg ${getSeverityColor(severity)}`}>
      <h4 className="font-semibold text-gray-900 mb-2">{title}</h4>
      <p className="text-sm text-gray-700 mb-3 italic">{assessment}</p>
      {children}
    </div>
  );
};

export default ResultsDisplay;
