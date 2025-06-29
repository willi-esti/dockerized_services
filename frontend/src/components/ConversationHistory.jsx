import React from 'react';
import { Clock, MessageCircle, ChevronRight } from 'lucide-react';

const ConversationHistory = ({ 
  conversations, 
  currentConversationId, 
  onSelectConversation, 
  isVisible, 
  onToggle 
}) => {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <>
      {/* Toggle button for mobile */}
      <button
        onClick={onToggle}
        className="lg:hidden fixed top-20 left-4 z-50 bg-white shadow-lg rounded-lg p-2 border"
      >
        <MessageCircle size={20} className="text-gray-600" />
      </button>

      {/* Overlay for mobile */}
      {isVisible && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:relative top-0 left-0 h-full bg-white border-r border-gray-200 z-50
        transition-transform duration-300 ease-in-out
        ${isVisible ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        w-80 lg:w-80 flex flex-col
      `}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
            <button
              onClick={onToggle}
              className="lg:hidden p-1 rounded-lg hover:bg-gray-100"
            >
              <ChevronRight size={20} className="text-gray-600" />
            </button>
          </div>
        </div>

        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <MessageCircle size={48} className="mx-auto mb-2 text-gray-300" />
              <p>No conversations yet</p>
              <p className="text-sm">Start a new chat to begin!</p>
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => onSelectConversation(conversation)}
                  className={`
                    w-full text-left p-3 rounded-lg transition-colors
                    ${conversation.id === currentConversationId
                      ? 'bg-blue-100 border-blue-200 border'
                      : 'hover:bg-gray-50 border border-transparent'
                    }
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate text-sm">
                        {conversation.title}
                      </h3>
                      <div className="flex items-center text-xs text-gray-500 mt-1">
                        <MessageCircle size={12} className="mr-1" />
                        <span>{conversation.message_count} messages</span>
                        <Clock size={12} className="ml-2 mr-1" />
                        <span>{formatDate(conversation.updated_at)}</span>
                      </div>
                    </div>
                    {conversation.id === currentConversationId && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 mt-1 flex-shrink-0" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ConversationHistory;
