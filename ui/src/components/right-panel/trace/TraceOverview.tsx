'use client';

import React from 'react';
import { format, formatDistanceToNow } from 'date-fns';
import { IoWarningOutline } from "react-icons/io5";
import ScatterPlot from '../../plot/Scatter';

interface TraceOverviewProps {
  // Single trace props
  traceQueryStartTime?: Date;
  traceQueryEndTime?: Date;
  // Multiple trace props
  traceIDs?: string[];  // Array of trace IDs
  traceStartTimes?: Date[];  // Array of trace start times
  traceEndTimes?: Date[];    // Array of trace end times
  traceDurations?: number[];  // Array of durations in milliseconds
  tracePercentiles?: string[]; // Array of percentiles for each trace (e.g. 'P90', 'P50', ...)
  // Callback props
  onTraceSelect?: (traceId: string) => void; // Add callback for trace selection
}

export default function TraceOverview({ 
  // Single trace props
  traceQueryStartTime,
  traceQueryEndTime,
  // Multiple trace props
  traceIDs = [],
  traceStartTimes = [],
  traceEndTimes = [],
  traceDurations = [],
  tracePercentiles = [],
  // Callback props
  onTraceSelect
}: TraceOverviewProps) {
  // Debug log

  const formatTimeRange = () => {
    // Handle single trace case
    if (traceQueryStartTime && traceQueryEndTime) {
      const startFormatted = format(traceQueryStartTime, 'MMM d, yyyy hh:mm:ss a');
      const endFormatted = format(traceQueryEndTime, 'MMM d, yyyy hh:mm:ss a');
      const timeAgo = formatDistanceToNow(traceQueryEndTime, { addSuffix: true });
      const duration = formatDistanceToNow(traceQueryStartTime, { addSuffix: false });

      return (
        <div className="space-y-1">
          <div className="flex items-center space-x-2 mt-5 mb-5">
            <div className="flex-1">
              <div className="font-mono text-xs text-gray-500 dark:text-gray-400">
                Start Time
              </div>
              <div className="text-md font-medium text-gray-900 dark:text-gray-100 mt-0.5">
                {startFormatted}
              </div>
            </div>
            <div className="flex items-center">
              <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
              <div className="mx-2 text-xs text-gray-500 dark:text-gray-400">
                {duration}
              </div>
              <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
            </div>
            <div className="flex-1 text-right">
              <div className="font-mono text-xs text-gray-500 dark:text-gray-400">
                End Time
              </div>
              <div className="text-md font-medium text-gray-900 dark:text-gray-100 mt-0.5">
                {endFormatted}
              </div>
            </div>
          </div>
          <div className="mt-5 text-xs text-gray-500 dark:text-gray-400 italic text-center">
            Last updated {timeAgo}
          </div>
        </div>
      );
    }

    // Handle multiple traces case
    if (traceStartTimes.length > 0 && traceEndTimes.length > 0) {
      const earliestStart = new Date(Math.min(...traceStartTimes.map(t => t.getTime())));
      const latestEnd = new Date(Math.max(...traceEndTimes.map(t => t.getTime())));

      const startFormatted = format(earliestStart, 'MMM d, yyyy hh:mm:ss a');
      const endFormatted = format(latestEnd, 'MMM d, yyyy hh:mm:ss a');
      const timeAgo = formatDistanceToNow(latestEnd, { addSuffix: true });
      const duration = formatDistanceToNow(earliestStart, { addSuffix: false });

      return (
        <div className="space-y-1">
          <div className="flex items-center space-x-2 mt-4">
            <div className="flex-1">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Earliest Trace Start
              </div>
              <div className="text-md font-medium text-gray-900 dark:text-gray-100 mt-1">
                {startFormatted}
              </div>
            </div>
            <div className="flex items-center">
              <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
              <div className="mx-2 text-xs text-gray-500 dark:text-gray-400">
                {duration}
              </div>
              <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
            </div>
            <div className="flex-1 text-right">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Latest Trace End
              </div>
              <div className="text-md font-medium text-gray-900 dark:text-gray-100 mt-1">
                {endFormatted}
              </div>
            </div>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 italic text-center">
            Last updated {timeAgo}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
            Showing {traceIDs.length} traces
          </div>
        </div>
      );
    }

    return null;
  };

  const renderScatterPlot = () => {
    if (traceStartTimes.length === 0 || traceDurations.length === 0) {
      return null;
    }

    const scatterData = traceStartTimes.map((startTime, index) => ({
      x: startTime,
      y: traceDurations[index],
      label: tracePercentiles[index] || 'default',
      traceId: traceIDs[index] // Include traceId for click handling
    }));

    const isPercentilePlot = tracePercentiles.length > 0;

    return (
      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <p className="font-mono text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center justify-center">Latency</p>
        <ScatterPlot
          data={scatterData}
          height={300}
          xAxisLabel="Trace Start Time"
          yAxisLabel="Latency (s)"
          isPercentilePlot={isPercentilePlot}
          onPointClick={onTraceSelect} // Pass the trace selection callback
        />
      </div>
    );
  };

  return (
    <div className="space-y-4 w-full p-4">
      <div className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 w-full">
        <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <p className="text-xl font-mono font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center justify-center">Query Time Range</p>
            {formatTimeRange()}
          </div>
          {renderScatterPlot()}
        </div>
      </div>
      <div className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-center items-center justify-center">
        <p className="text-gray-600 dark:text-gray-300 flex items-center text-center justify-center gap-2">
          <IoWarningOutline className="text-gray-500" size={20} />
          Select a trace from the list to view its tracing details.
        </p>
      </div>
    </div>
  );
}