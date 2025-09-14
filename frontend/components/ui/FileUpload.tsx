import { InputHTMLAttributes, forwardRef, useState } from 'react';
import { clsx } from 'clsx';
import { Upload, X, Zap } from 'lucide-react';

interface FileUploadProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
  helperText?: string;
  accept?: string;
  maxSize?: number; // in MB
  onFileChange?: (file: File | null) => void;
}

const FileUpload = forwardRef<HTMLInputElement, FileUploadProps>(
  ({ className, label, error, helperText, accept, maxSize = 10, onFileChange, id, ...props }, ref) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const inputId = id || `file-upload-${Math.random().toString(36).substr(2, 9)}`;

    const handleFileChange = (file: File | null) => {
      setSelectedFile(file);
      onFileChange?.(file);
    };

    const handleDrag = (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === 'dragenter' || e.type === 'dragover') {
        setDragActive(true);
      } else if (e.type === 'dragleave') {
        setDragActive(false);
      }
    };

    const handleDrop = (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        if (file.size <= maxSize * 1024 * 1024) {
          handleFileChange(file);
        }
      }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0] || null;
      if (file && file.size <= maxSize * 1024 * 1024) {
        handleFileChange(file);
      }
    };

    const removeFile = () => {
      handleFileChange(null);
    };

    return (
      <div className="w-full">
        {label && (
          <label className="label">
            {label}
          </label>
        )}
        
        <div
          className={clsx(
            'relative border-2 border-dashed rounded-sm p-6 transition-colors bg-mercury-700',
            {
              'border-mercury-500': dragActive,
              'border-silver-400 hover:border-silver-300': !dragActive && !selectedFile,
              'border-status-danger': error,
              'border-status-success': selectedFile && !error,
            }
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={ref}
            id={inputId}
            type="file"
            accept={accept}
            onChange={handleInputChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            {...props}
          />
          
          {selectedFile ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="h-5 w-5 text-status-success mr-2" />
                <span className="text-sm font-medium text-text-primary">
                  {selectedFile.name}
                </span>
                <span className="text-sm text-text-muted ml-2">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
              <button
                type="button"
                onClick={removeFile}
                className="text-text-muted hover:text-text-secondary"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-text-muted" />
              <div className="mt-4">
                <p className="text-sm text-text-secondary">
                  <span className="font-medium text-silver-300 hover:text-silver-200 cursor-pointer">
                    Click to upload
                  </span>{' '}
                  or drag and drop
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Max file size: {maxSize}MB
                </p>
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <p className="error-text">{error}</p>
        )}
        {helperText && !error && (
          <p className="helper-text">{helperText}</p>
        )}
      </div>
    );
  }
);

FileUpload.displayName = 'FileUpload';

export default FileUpload;
