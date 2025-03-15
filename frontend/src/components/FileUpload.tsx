import React, { useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import { useDropzone } from "react-dropzone";
import axios from "axios";

const CHUNK_SIZE = 1024 * 1024; // 1MB chunk size

const FileUpload: React.FC = () => {
    const [files, setFiles] = useState<File[]>([]);
    const [uploadProgress, setUploadProgress] = useState<number>(0);

    const onDrop = (acceptedFiles: File[]) => {
        setFiles(acceptedFiles);
        setUploadProgress(0);
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        multiple: true,
        accept: {
            "image/*": [],
            "application/pdf": [],
            "text/plain": [],
        },
    });

    /**
     * Uploads file in chunks
     * @param file - The file to be uploaded
     */
    // const uploadFileInChunks = async (file: File) => {
    //     const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    //     const fileId = `${file.name}-${Date.now()}`; // Unique file identifier

    //     // Step 1: Send metadata to backend
    //     try {
    //         await axios.post("http://localhost:7001/upload/metadata", {
    //             fileName: file.name,
    //             fileSize: file.size,
    //             totalChunks,
    //             fileId
    //         });
    //     } catch (error) {
    //         console.error("Error sending metadata:", error);
    //         alert("Failed to send metadata");
    //         return;
    //     }

    //     // Step 2: Upload chunks
    //     for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
    //         const start = chunkIndex * CHUNK_SIZE;
    //         const end = Math.min(start + CHUNK_SIZE, file.size);
    //         const chunk = file.slice(start, end);

    //         const formData = new FormData();
    //         formData.append("fileId", fileId);
    //         formData.append("chunkIndex", chunkIndex.toString());
    //         formData.append("chunk", chunk);

    //         try {
    //             await axios.post("http://localhost:7001/upload/chunk", formData, {
    //                 headers: { "Content-Type": "multipart/form-data" },
    //                 withCredentials: true
    //             });

    //             // Update progress
    //             setUploadProgress(Math.round(((chunkIndex + 1) / totalChunks) * 100));

    //         } catch (error) {
    //             console.error("Chunk upload failed:", error);
    //             alert("Upload failed, please try again.");
    //             return;
    //         }
    //     }

    //     // Step 3: Notify backend that upload is complete
    //     try {
    //         await axios.post("http://localhost:7001/upload/complete", { fileId });
    //         alert("Upload completed!");
    //     } catch (error) {
    //         console.error("Error finalizing upload:", error);
    //         alert("Upload finalization failed");
    //     }
    // };

    const uploadFileInChunks = async (file: File) => {
        const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
        const fileId = `${file.name}-${Date.now()}`;

        console.log(`📌 Uploading ${file.name} in ${totalChunks} chunks`);

        for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
            const start = chunkIndex * CHUNK_SIZE;
            const end = Math.min(start + CHUNK_SIZE, file.size);
            const chunk = file.slice(start, end);

            console.log(`📤 Sending chunk ${chunkIndex}: bytes [${start} - ${end}]`);

            const formData = new FormData();
            formData.append("fileId", fileId);
            formData.append("chunkIndex", chunkIndex.toString());
            formData.append("chunk", chunk);
            formData.append("totalChunks", totalChunks.toString());

            try {
                await axios.post("http://localhost:7001/upload/chunk", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                    withCredentials: true
                });

                setUploadProgress(Math.round(((chunkIndex + 1) / totalChunks) * 100));

            } catch (error) {
                console.error("❌ Chunk upload failed:", error);
                alert("Upload failed, please try again.");
                return;
            }
        }
        const uploadFileInChunks = async (file: File) => {
            const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
            const fileId = `${file.name}-${Date.now()}`;

            for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
                const start = chunkIndex * CHUNK_SIZE;
                const end = Math.min(start + CHUNK_SIZE, file.size);
                const chunk = file.slice(start, end);

                const formData = new FormData();
                formData.append("fileId", fileId);
                formData.append("chunkIndex", chunkIndex.toString());
                formData.append("chunk", chunk);
                formData.append("totalChunks", totalChunks.toString());

                try {
                    await axios.post("http://localhost:7001/upload/chunk", formData, {
                        headers: { "Content-Type": "multipart/form-data" },
                        withCredentials: true
                    });

                    setUploadProgress(Math.round(((chunkIndex + 1) / totalChunks) * 100));
                } catch (error) {
                    alert("Upload failed, please try again.");
                    return;
                }
            }
        };

        // Step 3: Notify backend that upload is complete
        try {
            await axios.post("http://localhost:7001/upload/complete", { fileId });
            alert("Upload completed!");
        } catch (error) {
            console.error("Error finalizing upload:", error);
            alert("Upload finalization failed");
        }
    };

    const handleUpload = () => {
        if (files.length === 0) {
            alert("Please select a file to upload.");
            return;
        }

        // Upload each file in chunks
        files.forEach(uploadFileInChunks);
    };

    return (
        <Box sx={{ width: "50%", margin: "auto", textAlign: "center", mt: 4, p: 2, border: "1px dashed #aaa" }}>
            <Typography variant="h4" sx={{ textAlign: "center", mb: 2 }}>
                File Upload System
            </Typography>

            <Box {...getRootProps()} sx={{ p: 3, backgroundColor: "#f8f8f8", border: "2px dashed #007bff", cursor: "pointer" }}>
                <input {...getInputProps()} />
                <Typography>Drag & drop files here, or click to select</Typography>
            </Box>

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

            {uploadProgress > 0 && (
                <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography>{uploadProgress}%</Typography>
                </Box>
            )}

            <Button variant="contained" color="primary" onClick={handleUpload} sx={{ mt: 2 }} disabled={files.length === 0}>
                Upload
            </Button>
        </Box>
    );
};

export default FileUpload;
