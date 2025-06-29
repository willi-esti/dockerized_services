import React from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';

const TokenUsage = ({ tokenUsage, isVisible = true }) => {
  if (!tokenUsage || !isVisible) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'critical': return <XCircle className="w-4 h-4" />;
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Info className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const getProgressBarColor = (status) => {
    switch (status) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const colorClasses = getStatusColor(tokenUsage.status);
  const progressColor = getProgressBarColor(tokenUsage.status);

  return (
    <div className={`mt-2 p-3 rounded-lg border text-xs ${colorClasses}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon(tokenUsage.status)}
          <span className="font-semibold">Token Usage</span>
        </div>
        <span className="font-mono">
          {tokenUsage.used_tokens.toLocaleString()}/{tokenUsage.max_tokens.toLocaleString()}
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${progressColor}`}
          style={{ width: `${Math.min(tokenUsage.usage_percentage, 100)}%` }}
        ></div>
      </div>
      
      <div className="flex justify-between items-center text-xs">
        <span>{tokenUsage.usage_percentage}% of context window</span>
        <span className="opacity-75">{tokenUsage.model_name}</span>
      </div>
      
      {/* Token breakdown */}
      {tokenUsage.token_breakdown && (
        <details className="mt-2">
          <summary className="cursor-pointer hover:opacity-75 select-none">
            Token breakdown
          </summary>
          <div className="mt-1 pl-4 space-y-1 text-xs opacity-75">
            <div>System prompt: {tokenUsage.token_breakdown.system} tokens</div>
            <div>Conversation context: {tokenUsage.token_breakdown.context} tokens</div>
            <div>Your message: {tokenUsage.token_breakdown.message} tokens</div>
            <div>Overhead: {tokenUsage.token_breakdown.overhead} tokens</div>
          </div>
        </details>
      )}
      
      {/* Warning messages */}
      {tokenUsage.status === 'critical' && (
        <div className="mt-2 text-xs font-medium">
          ⚠️ Context window nearly full! Consider starting a new conversation.
        </div>
      )}
      {tokenUsage.status === 'high' && (
        <div className="mt-2 text-xs font-medium">
          📊 High token usage. AI responses may become less reliable.
        </div>
      )}
    </div>
  );
};

export default TokenUsage;
