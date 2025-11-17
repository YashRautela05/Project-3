# Results Display Component

## Overview

A comprehensive, user-friendly component that displays crime detection analysis results in an organized and visually appealing format. The component automatically shows when the analysis status is "done".

## Features

### 🎯 Smart Display Sections

1. **Critical Alert Header**
   - Severity level with color coding (Critical/High/Medium/Low)
   - Crime detection status badge
   - Immediate safety recommendations
   - Crime indicators with confidence scores

2. **AI Analysis Summary (Gemini)**
   - Natural language description of findings
   - Crime type and severity
   - Evidence list
   - Safety recommendations with emergency contact info
   - IPC (Indian Penal Code) section suggestions
   - Legal disclaimer

3. **Quick Statistics Dashboard**
   - Frames analyzed
   - Unique objects detected
   - Events detected
   - Processing FPS

4. **Detailed Crime Analysis**
   - **Weapon Threat Analysis**: Frame-by-frame weapon detections, proximity alerts
   - **Violence Analysis**: Violence score with progress bar, violent actions detected
   - **Theft Analysis**: Theft probability, valuable item disappearances
   - **Suspicious Behavior**: Patterns like loitering with confidence scores

5. **Object Detection Summary**
   - List of unique objects detected (pills/badges)
   - Sample detections from first 4 frames
   - Object confidence scores

6. **Motion Analysis**
   - Average/max motion metrics
   - Motion pattern categorization
   - Crime relevance assessment

7. **Action Recognition**
   - Top actions detected per clip
   - Crime-relevant actions highlighted
   - Probability visualization with progress bars

8. **Events Timeline**
   - Chronological event list
   - Severity-based color coding
   - Frame-specific details

9. **Analysis Metadata**
   - Task ID
   - Video hash
   - Analysis version
   - Models used (YOLOv8x, MoViNet, etc.)

## Color Coding System

### Severity Levels
- **Critical**: Red (`bg-red-100 border-red-300 text-red-600`)
- **High**: Orange (`bg-orange-100 border-orange-300 text-orange-600`)
- **Medium/Moderate**: Yellow (`bg-yellow-100 border-yellow-300 text-yellow-600`)
- **Low**: Green (`bg-green-100 border-green-300 text-green-600`)

### Status Indicators
- **Crime Detected**: Red badge
- **No Crime**: Green badge
- **Crime-Relevant Actions**: Red background highlight

## Component Structure

```typescript
interface ResultsDisplayProps {
  data: {
    task_id: string;
    status: string;
    result: {
      summary: {...};
      crime_report: {...};
      gemini_output: {...};
      events: [...];
      metadata: {...};
    }
  }
}
```

## Interactive Features

### Collapsible Sections
All major sections can be expanded/collapsed for better navigation:
- ✅ Summary (expanded by default)
- ✅ Crime Report (expanded by default)
- ✅ Gemini Analysis (expanded by default)
- Object Detections (collapsed by default)
- Actions (collapsed by default)
- Motion (collapsed by default)
- Events (collapsed by default)

### Section Toggle
Click on any section header to expand/collapse it.

## Usage

### In Upload.tsx

The component is automatically displayed when analysis completes:

```typescript
// When status is 'done', the ResultsDisplay component is shown
if (analysisResult && analysisResult.status === 'done') {
  return (
    <div className="space-y-6">
      <motion.div className="flex items-center justify-between">
        <h1>Analysis Results</h1>
        <button onClick={handleNewAnalysis}>
          <ArrowLeft /> New Analysis
        </button>
      </motion.div>
      <ResultsDisplay data={analysisResult} />
    </div>
  );
}
```

### Navigation Flow

1. User uploads video → Upload status shown
2. Processing → Progress indicators
3. Analysis complete → ResultsDisplay automatically appears
4. "New Analysis" button → Returns to upload screen

## Visual Elements

### Icons Used
- `AlertTriangle`: Warnings and crime indicators
- `Shield`: Security and safety
- `Activity`: Motion and actions
- `Eye`: Object detection
- `Target`: Object tracking
- `Clock`: Time-based metrics
- `Phone`: Emergency recommendations
- `FileText`: Evidence
- `Zap`: AI analysis
- `CheckCircle`/`XCircle`: Status indicators

### Animations
- Sections fade in with stagger effect using Framer Motion
- Smooth expand/collapse transitions
- Progress bars for scores and probabilities

## Key Highlights

### Safety First Design
- Critical alerts prominently displayed at top
- Emergency recommendations highlighted in red
- Clear call-to-action for emergencies (Call 911/112)

### Data Visualization
- Progress bars for violence scores
- Confidence percentages
- Color-coded severity levels
- Badge-style tags for quick scanning

### Comprehensive Information
- Shows all detection results
- Frame-specific details
- Proximity alerts for weapons
- Object persistence tracking
- Multi-person scene analysis

### User-Friendly Layout
- Clean card-based design
- Responsive grid layouts
- Clear typography hierarchy
- Intuitive section organization

## Example Data Flow

```
Video Upload
    ↓
Processing (Polling)
    ↓
Status: 'done'
    ↓
ResultsDisplay Component
    ├─ Alert Header (Critical/High/Medium/Low)
    ├─ Gemini AI Summary
    ├─ Quick Stats
    ├─ Crime Analysis Details
    │   ├─ Weapon Threats
    │   ├─ Violence
    │   ├─ Theft
    │   └─ Suspicious Behavior
    ├─ Object Detections
    ├─ Motion Analysis
    ├─ Action Recognition
    ├─ Events Timeline
    └─ Metadata
```

## Accessibility

- Semantic HTML structure
- Clear visual hierarchy
- Color coding with text labels (not just color)
- Keyboard navigable (collapsible sections)
- Screen reader friendly content

## Performance

- Sections collapsed by default to reduce initial render
- Efficient state management
- Memoized components where applicable
- Smooth animations with Framer Motion

## Customization

### Adding New Sections
```typescript
// Add to expandedSections state
const [expandedSections, setExpandedSections] = useState({
  // ... existing sections
  newSection: false, // Add your section
});

// Use CollapsibleSection component
<CollapsibleSection
  title="Your Section Title"
  icon={<YourIcon />}
  isExpanded={expandedSections.newSection}
  onToggle={() => toggleSection('newSection')}
>
  {/* Your content */}
</CollapsibleSection>
```

### Modifying Color Scheme
Edit the `getSeverityColor()` function to customize colors for different severity levels.

## Dependencies

- React
- Framer Motion (animations)
- Lucide React (icons)
- Tailwind CSS (styling)

## Future Enhancements

- [ ] Export results to PDF
- [ ] Download detailed report
- [ ] Share results functionality
- [ ] Frame image previews
- [ ] Video playback with timestamp markers
- [ ] Filter/search events
- [ ] Comparison with previous analyses
- [ ] Custom severity thresholds

## Notes

- All percentages are rounded for readability
- Frame indices are 0-based
- Confidence scores displayed as percentages
- Video hash truncated for display (first 16 chars)
- Model names and versions shown in metadata

## Support

For issues or questions about the ResultsDisplay component, check:
- Component code: `src/components/ResultsDisplay.tsx`
- Integration: `src/pages/Upload.tsx`
- Styling: Tailwind CSS classes (custom styles in `index.css`)
