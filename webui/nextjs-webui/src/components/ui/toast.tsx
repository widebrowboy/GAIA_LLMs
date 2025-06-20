'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { notificationVariants } from '@/utils/animations';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Info, 
  X,
  ExternalLink
} from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  persistent?: boolean;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

interface ToastProviderProps {
  children: ReactNode;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxToasts?: number;
}

export function ToastProvider({ 
  children, 
  position = 'top-right',
  maxToasts = 5 
}: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: Toast = {
      id,
      duration: 4000,
      ...toast,
    };

    setToasts(prev => {
      const updated = [newToast, ...prev];
      return updated.slice(0, maxToasts);
    });

    // Auto remove after duration (unless persistent)
    if (!newToast.persistent && newToast.duration) {
      setTimeout(() => {
        removeToast(id);
      }, newToast.duration);
    }
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const clearAll = () => {
    setToasts([]);
  };

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2',
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearAll }}>
      {children}
      <div className={`fixed z-50 flex flex-col space-y-2 ${positionClasses[position]}`}>
        <AnimatePresence>
          {toasts.map(toast => (
            <ToastComponent 
              key={toast.id} 
              toast={toast} 
              onRemove={() => removeToast(toast.id)} 
            />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

interface ToastComponentProps {
  toast: Toast;
  onRemove: () => void;
}

function ToastComponent({ toast, onRemove }: ToastComponentProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getToastStyles = (type: ToastType) => {
    const styles = {
      success: {
        bg: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
        icon: CheckCircle,
        iconColor: 'text-green-500',
        titleColor: 'text-green-800 dark:text-green-200',
        messageColor: 'text-green-600 dark:text-green-300',
      },
      error: {
        bg: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
        icon: XCircle,
        iconColor: 'text-red-500',
        titleColor: 'text-red-800 dark:text-red-200',
        messageColor: 'text-red-600 dark:text-red-300',
      },
      warning: {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
        icon: AlertCircle,
        iconColor: 'text-yellow-500',
        titleColor: 'text-yellow-800 dark:text-yellow-200',
        messageColor: 'text-yellow-600 dark:text-yellow-300',
      },
      info: {
        bg: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
        icon: Info,
        iconColor: 'text-blue-500',
        titleColor: 'text-blue-800 dark:text-blue-200',
        messageColor: 'text-blue-600 dark:text-blue-300',
      },
    };
    return styles[type];
  };

  const styles = getToastStyles(toast.type);
  const IconComponent = styles.icon;

  return (
    <motion.div
      className={`
        min-w-80 max-w-md p-4 rounded-lg border shadow-lg backdrop-blur-sm
        ${styles.bg}
      `}
      variants={notificationVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      layout
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <IconComponent className={`h-5 w-5 ${styles.iconColor}`} />
        </div>
        
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${styles.titleColor}`}>
            {toast.title}
          </h3>
          
          {toast.message && (
            <p className={`mt-1 text-sm ${styles.messageColor}`}>
              {toast.message}
            </p>
          )}
          
          {toast.action && (
            <div className="mt-3">
              <button
                onClick={toast.action.onClick}
                className={`
                  inline-flex items-center text-sm font-medium rounded-md px-3 py-1
                  ${styles.titleColor} hover:bg-black/5 dark:hover:bg-white/5
                  transition-colors duration-200
                `}
              >
                {toast.action.label}
                <ExternalLink className="ml-1 h-3 w-3" />
              </button>
            </div>
          )}
        </div>
        
        <div className="ml-4 flex-shrink-0">
          <button
            onClick={onRemove}
            className={`
              inline-flex rounded-md p-1.5 transition-colors duration-200
              ${styles.messageColor} hover:bg-black/10 dark:hover:bg-white/10
            `}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      {/* Progress bar for auto-dismiss */}
      {!toast.persistent && toast.duration && (
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg"
          initial={{ width: '100%' }}
          animate={{ 
            width: isHovered ? '100%' : '0%' 
          }}
          transition={{ 
            duration: isHovered ? 0 : (toast.duration / 1000),
            ease: 'linear'
          }}
        />
      )}
    </motion.div>
  );
}

// Convenience functions for different toast types
export const toast = {
  success: (title: string, message?: string, options?: Partial<Toast>) => ({
    type: 'success' as const,
    title,
    message,
    ...options,
  }),
  
  error: (title: string, message?: string, options?: Partial<Toast>) => ({
    type: 'error' as const,
    title,
    message,
    ...options,
  }),
  
  warning: (title: string, message?: string, options?: Partial<Toast>) => ({
    type: 'warning' as const,
    title,
    message,
    ...options,
  }),
  
  info: (title: string, message?: string, options?: Partial<Toast>) => ({
    type: 'info' as const,
    title,
    message,
    ...options,
  }),
};

// Hook for common toast operations
export function useToastHelpers() {
  const { addToast } = useToast();

  return {
    success: (title: string, message?: string, options?: Partial<Toast>) => 
      addToast(toast.success(title, message, options)),
    
    error: (title: string, message?: string, options?: Partial<Toast>) => 
      addToast(toast.error(title, message, options)),
    
    warning: (title: string, message?: string, options?: Partial<Toast>) => 
      addToast(toast.warning(title, message, options)),
    
    info: (title: string, message?: string, options?: Partial<Toast>) => 
      addToast(toast.info(title, message, options)),
    
    // AI-specific toasts
    aiStarted: (mode: string) => 
      addToast(toast.info('AI 모드 전환', `${mode} 모드로 전환되었습니다.`)),
    
    mcpConnected: (serverName: string) => 
      addToast(toast.success('MCP 연결', `${serverName} 서버에 연결되었습니다.`)),
    
    mcpError: (serverName: string, error: string) => 
      addToast(toast.error('MCP 오류', `${serverName}: ${error}`, { persistent: true })),
    
    copySuccess: () => 
      addToast(toast.success('복사 완료', '클립보드에 복사되었습니다.', { duration: 2000 })),
    
    saveSuccess: (filename: string) => 
      addToast(toast.success('저장 완료', `${filename}이 저장되었습니다.`)),
    
    exportReady: (format: string, action: () => void) => 
      addToast(toast.success(
        '내보내기 준비', 
        `${format} 형식으로 준비되었습니다.`,
        { 
          action: { label: '다운로드', onClick: action },
          duration: 10000 
        }
      )),
  };
}