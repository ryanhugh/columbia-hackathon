import React, { useEffect } from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  onClose?: () => void;
  autoClose?: number;
}

export default function ErrorAlert({
  message,
  onClose,
  autoClose = 5000,
}: ErrorAlertProps) {
  useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, autoClose);
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose]);

  return (
    <div className="fixed bottom-4 right-4 max-w-md bg-red-900/20 border border-red-600 rounded-lg p-4 flex items-start gap-3 animate-in">
      <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
      <div className="flex-1">
        <p className="text-red-300 text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-red-500 hover:text-red-400 flex-shrink-0"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}
