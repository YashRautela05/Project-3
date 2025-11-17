# Debugging Results Page Not Showing Data

## Changes Made

1. **Added console logging in Results.tsx**:
   - Logs the full API response
   - Logs when analysis is complete

2. **Added null checking in ResultsDisplay.tsx**:
   - Checks if `data` exists
   - Checks if `data.result` exists
   - Checks if required fields (`summary`, `crime_report`) exist
   - Shows helpful error messages with the actual data received

## How to Debug

1. **Open Browser Developer Tools** (F12 or Right-click > Inspect)

2. **Go to Console Tab**

3. **Navigate to the results page**: `/results/b1a744f9-206c-446a-a0a6-455e3d9a58c6`

4. **Look for these console messages**:
   - "API Response:" - This shows what the backend is returning
   - "Analysis complete, setting result:" - This shows what React is storing

5. **Check if you see**:
   - Yellow warning box saying "Invalid Data" or "Incomplete Analysis Results"
   - If so, the data structure doesn't match what we expect

## Expected Data Structure

The API should return:
```json
{
  "task_id": "...",
  "status": "done",
  "result": {
    "summary": { ... },
    "crime_report": { ... },
    "gemini_output": { ... },
    ...
  }
}
```

The `ResultsDisplay` component expects to receive this entire object and will access `data.result`.

## Common Issues

### Issue 1: API returns different structure
**Symptom**: Yellow warning box with data preview
**Solution**: Check the console logs to see actual API response structure

### Issue 2: Page stays in loading state
**Symptom**: Forever shows "Loading Analysis Results..."
**Solution**: 
- Check if API endpoint is running (http://localhost:8000/status/{taskId})
- Check network tab for failed requests
- Verify taskId is correct in URL

### Issue 3: Shows error state
**Symptom**: Red error box
**Solution**: Check console for error messages from axios

## Quick Test

Run this in the browser console when on the results page:
```javascript
fetch('http://localhost:8000/status/b1a744f9-206c-446a-a0a6-455e3d9a58c6')
  .then(r => r.json())
  .then(data => console.log('Direct API test:', data))
  .catch(err => console.error('API Error:', err));
```

This will show you exactly what the API is returning.
