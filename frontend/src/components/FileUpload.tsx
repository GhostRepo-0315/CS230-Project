import React, { useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import { useDropzone } from "react-dropzone";
import axios from "axios";

/**
 * Component for uploading files with drag & drop support.
 * Includes a progress bar for better user experience.
 */
const FileUpload: React.FC = () => {
    const [files, setFiles] = useState<File[]>([]); // Store selected files
    const [uploadProgress, setUploadProgress] = useState<number>(0); // Upload progress

    /**
     * Handles file selection using drag & drop or manual selection.
     * @param acceptedFiles - Array of selected files
     */
    const onDrop = (acceptedFiles: File[]) => {
        setFiles(acceptedFiles);
        setUploadProgress(0); // Reset progress when new files are added
    };

    // React Dropzone hook for handling drag & drop
    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        multiple: true, // Allow multiple file uploads
        accept: {
            "image/*": [], // Allow all image files
            "application/pdf": [], // Allow PDFs
            "text/plain": [], // Allow text files
        },
    });

    /**
     * Handles the file upload process.
     * Uses axios to send files to the backend and tracks upload progress.
     */
    const handleUpload = async () => {
        if (files.length === 0) {
            alert("Please select a file to upload.");
            return;
        }
    
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));
    
        try {
            // Send the file to the backend and store the response
            const response = await axios.post("http://localhost:7001/upload", formData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
                withCredentials: true, // Ensure cookies and CORS headers are sent
              });

            console.log("Server Response:", response.data); // Debug log to check response
            alert("Upload successful!");
    
        } catch (error) {
            console.error("Upload failed:", error);
            alert("Upload failed. Please try again.");
        }
    };
    

    return (
        <Box sx={{ width: "50%", margin: "auto", textAlign: "center", mt: 4, p: 2, border: "1px dashed #aaa" }}>
            <Typography variant="h4" sx={{ textAlign: "center", mb: 2 }}>
                File Upload System
            </Typography>

            {/* Drag & Drop Area */}
            <Box {...getRootProps()} sx={{ p: 3, backgroundColor: "#f8f8f8", border: "2px dashed #007bff", cursor: "pointer" }}>
                <input {...getInputProps()} />
                <Typography>Drag & drop files here, or click to select</Typography>
            </Box>

            {/* Selected File List */}
            {files.length > 0 && (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle1">Selected Files:</Typography>
                    {files.map((file, index) => (
                        <Typography key={index} sx={{ fontSize: "14px", color: "#333" }}>
                            {file.name} ({(file.size / 1024).toFixed(2)} KB)
                        </Typography>
                    ))}
                </Box>
            )}

            {/* Upload Progress Bar */}
            {uploadProgress > 0 && (
                <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography>{uploadProgress}%</Typography>
                </Box>
            )}

            {/* Upload Button */}
            <Button variant="contained" color="primary" onClick={handleUpload} sx={{ mt: 2 }} disabled={files.length === 0}>
                Upload
            </Button>
        </Box>
    );
};

export default FileUpload;
