import React, { useState } from 'react';
import { Upload } from 'lucide-react';

interface ModelUploadProps {
  onUpload: (file: File) => void;
}

export const ModelUpload: React.FC<ModelUploadProps> = ({ onUpload }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Upload size={24} /> Upload Model
      </h2>
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
        }`}
      >
        <Upload size={48} className="mx-auto mb-4 text-gray-400" />
        <p className="text-lg font-semibold mb-2">Drag and drop your model</p>
        <p className="text-gray-600 mb-4">or click to select</p>
        <input
          type="file"
          onChange={handleChange}
          accept=".pb,.tflite,.onnx,.pt,.pth,.h5"
          className="hidden"
          id="model-input"
        />
        <label htmlFor="model-input" className="btn-primary inline-block cursor-pointer">
          Select File
        </label>
      </div>
      <p className="text-sm text-gray-500 mt-4">
        Supported: .pb, .tflite, .onnx, .pt, .pth, .h5
      </p>
    </div>
  );
};
