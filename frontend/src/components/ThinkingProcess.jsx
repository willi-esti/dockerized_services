import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, Search, FileText, Clock, CheckCircle, AlertCircle, HelpCircle, Zap, XCircle } from 'lucide-react';

const ThinkingProcess = ({ steps, isVisible = false }) => {
  const [isExpanded, setIsExpanded] = useState(isVisible);

  if (!steps || steps.length === 0) return null;

  const getStepIcon = (type) => {
    switch (type) {
      case 'ai_thinking': return <Brain className="w-4 h-4 text-purple-600" />;
      case 'ai_decision': return <Zap className="w-4 h-4 text-blue-600" />;
      case 'database_search': return <Search className="w-4 h-4 text-green-600" />;
      case 'multi_search': return <Search className="w-4 h-4 text-green-600" />;
      case 'context_building': return <FileText className="w-4 h-4 text-orange-600" />;
      case 'final_response': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'clarification_needed': return <HelpCircle className="w-4 h-4 text-yellow-600" />;
      case 'no_results': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'max_iterations': return <Clock className="w-4 h-4 text-gray-600" />;
      default: return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStepColor = (type) => {
    switch (type) {
      case 'ai_thinking': return 'border-purple-200 bg-purple-50';
      case 'ai_decision': return 'border-blue-200 bg-blue-50';
      case 'database_search': return 'border-green-200 bg-green-50';
      case 'multi_search': return 'border-green-200 bg-green-50';
      case 'context_building': return 'border-orange-200 bg-orange-50';
      case 'final_response': return 'border-green-200 bg-green-50';
      case 'clarification_needed': return 'border-yellow-200 bg-yellow-50';
      case 'no_results': return 'border-red-200 bg-red-50';
      case 'error': return 'border-red-200 bg-red-50';
      case 'max_iterations': return 'border-gray-200 bg-gray-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="mt-2 border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 transition-colors flex items-center justify-between text-sm text-gray-700"
      >
        <div className="flex items-center space-x-2">
          <Brain className="w-4 h-4" />
          <span>AI Thinking Process ({steps.length} steps)</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      
      {isExpanded && (
        <div className="p-3 space-y-3 max-h-96 overflow-y-auto">
          {steps.map((step, index) => (
            <div key={index} className={`border rounded-lg p-3 ${getStepColor(step.type)}`}>
              <div className="flex items-start space-x-2">
                <div className="flex-shrink-0 mt-0.5">
                  {getStepIcon(step.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">
                      {step.title}
                    </h4>
                    <span className="text-xs text-gray-500">
                      Step {step.step}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mt-1">
                    {step.description}
                  </p>
                  
                  {step.reasoning && (
                    <div className="mt-2 p-2 bg-white bg-opacity-50 rounded text-xs">
                      <span className="font-medium">Reasoning: </span>
                      {step.reasoning}
                    </div>
                  )}
                  
                  {step.search_query && (
                    <div className="mt-2 space-y-1">
                      <div className="text-xs">
                        <span className="font-medium">Query: </span>
                        <code className="bg-white bg-opacity-70 px-1 rounded">
                          {step.search_query}
                        </code>
                      </div>
                      {step.results_count !== undefined && (
                        <div className="text-xs">
                          <span className="font-medium">Results: </span>
                          {step.results_count} found
                        </div>
                      )}
                    </div>
                  )}
                  
                  {step.results_preview && step.results_preview.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs font-medium mb-1">Preview:</div>
                      <div className="space-y-1">
                        {step.results_preview.map((result, idx) => (
                          <div key={idx} className="text-xs bg-white bg-opacity-70 p-2 rounded">
                            <div className="text-gray-800">{result.content}</div>
                            {result.similarity && (
                              <div className="text-gray-500 mt-1">
                                Similarity: {result.similarity}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {step.searches && (
                    <div className="mt-2">
                      <div className="text-xs font-medium mb-1">Multiple Searches:</div>
                      <div className="space-y-1">
                        {step.searches.map((search, idx) => (
                          <div key={idx} className="text-xs bg-white bg-opacity-70 p-2 rounded">
                            <div>
                              <span className="font-medium">Query: </span>
                              <code>{search.query}</code>
                            </div>
                            <div>
                              <span className="font-medium">Type: </span>
                              {search.type}
                            </div>
                            <div>
                              <span className="font-medium">Results: </span>
                              {search.results_count}
                            </div>
                            {search.preview && search.preview.length > 0 && (
                              <div className="mt-1 text-gray-600">
                                {search.preview.map((p, pidx) => (
                                  <div key={pidx}>• {p}</div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {step.question && (
                    <div className="mt-2 p-2 bg-white bg-opacity-50 rounded text-xs">
                      <span className="font-medium">Question: </span>
                      {step.question}
                    </div>
                  )}
                  
                  <div className="mt-2 text-xs text-gray-500">
                    {new Date(step.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThinkingProcess;
