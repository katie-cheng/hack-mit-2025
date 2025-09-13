import { InputHTMLAttributes, forwardRef, useState } from 'react';
import { clsx } from 'clsx';
import { Upload, X } from 'lucide-react';

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
            'relative border-2 border-dashed rounded-lg p-6 transition-colors',
            {
              'border-primary-300 bg-primary-50': dragActive,
              'border-gray-300 hover:border-gray-400': !dragActive && !selectedFile,
              'border-danger-300 bg-danger-50': error,
              'border-success-300 bg-success-50': selectedFile && !error,
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
                <Upload className="h-5 w-5 text-success-600 mr-2" />
                <span className="text-sm font-medium text-gray-900">
                  {selectedFile.name}
                </span>
                <span className="text-sm text-gray-500 ml-2">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
              <button
                type="button"
                onClick={removeFile}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  <span className="font-medium text-primary-600 hover:text-primary-500 cursor-pointer">
                    Click to upload
                  </span>{' '}
                  or drag and drop
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Max file size: {maxSize}MB
                </p>
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1 text-sm text-danger-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

FileUpload.displayName = 'FileUpload';

export default FileUpload;
