import { useState, useRef, useCallback } from "react";
import { Upload, X, Camera, Loader2, CheckCircle, AlertCircle } from "lucide-react";

/**
 * ScreenshotUpload - Drag & drop image upload component for OCR processing.
 * Props:
 *   mode: "assets" | "trades"
 *   onExtracted: (data) => void  - called with extracted data on success
 *   onClose: () => void
 */
export default function ScreenshotUpload({ mode = "assets", onExtracted, onClose }) {
    const [dragging, setDragging] = useState(false);
    const [preview, setPreview] = useState(null);
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("idle"); // idle | uploading | success | error
    const [errorMsg, setErrorMsg] = useState("");
    const inputRef = useRef(null);

    const endpoint = mode === "assets"
        ? "http://localhost:8000/api/ocr/extract-assets"
        : "http://localhost:8000/api/ocr/extract-trades";

    const modeLabel = mode === "assets" ? "보유 자산" : "거래 내역";

    const handleFile = (f) => {
        if (!f) return;
        if (!f.type.startsWith("image/")) {
            setErrorMsg("이미지 파일만 업로드 가능합니다.");
            setStatus("error");
            return;
        }
        setFile(f);
        setStatus("idle");
        setErrorMsg("");
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(f);
    };

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragging(false);
        const f = e.dataTransfer.files[0];
        handleFile(f);
    }, []);

    const handleDragOver = (e) => { e.preventDefault(); setDragging(true); };
    const handleDragLeave = () => setDragging(false);

    const handleAnalyze = async () => {
        if (!file) return;
        setStatus("uploading");
        setErrorMsg("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(endpoint, { method: "POST", body: formData });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "분석 실패");
            }
            const data = await res.json();
            setStatus("success");
            onExtracted(data);
        } catch (e) {
            setStatus("error");
            setErrorMsg(e.message);
        }
    };

    const reset = () => {
        setFile(null);
        setPreview(null);
        setStatus("idle");
        setErrorMsg("");
    };

    return (
        <div className="ocr-upload-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="ocr-upload-modal">
                {/* Header */}
                <div className="ocr-header">
                    <div className="ocr-title">
                        <Camera size={20} />
                        <span>스크린샷으로 {modeLabel} 추가</span>
                    </div>
                    <button className="ocr-close-btn" onClick={onClose}><X size={18} /></button>
                </div>

                <p className="ocr-subtitle">
                    증권사 앱에서 {modeLabel} 화면을 캡처한 후 업로드하면 자동으로 인식합니다.
                </p>

                {/* Drop Zone */}
                {!preview ? (
                    <div
                        className={`ocr-dropzone ${dragging ? "dragging" : ""}`}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onClick={() => inputRef.current?.click()}
                    >
                        <Upload size={40} className="ocr-drop-icon" />
                        <p className="ocr-drop-text">이미지를 드래그하거나 클릭하여 업로드</p>
                        <p className="ocr-drop-hint">JPEG, PNG, WebP 지원 · 최대 10MB</p>
                        <input
                            ref={inputRef}
                            type="file"
                            accept="image/*"
                            style={{ display: "none" }}
                            onChange={(e) => handleFile(e.target.files[0])}
                        />
                    </div>
                ) : (
                    <div className="ocr-preview-container">
                        <img src={preview} alt="preview" className="ocr-preview-img" />
                        <button className="ocr-reset-btn" onClick={reset}>
                            <X size={14} /> 다시 선택
                        </button>
                    </div>
                )}

                {/* Status Messages */}
                {status === "error" && (
                    <div className="ocr-status error">
                        <AlertCircle size={16} />
                        <span>{errorMsg}</span>
                    </div>
                )}
                {status === "success" && (
                    <div className="ocr-status success">
                        <CheckCircle size={16} />
                        <span>인식 완료! 아래에서 내용을 확인하고 수정하세요.</span>
                    </div>
                )}

                {/* Actions */}
                <div className="ocr-actions">
                    <button className="ocr-cancel-btn" onClick={onClose}>취소</button>
                    <button
                        className="ocr-analyze-btn"
                        onClick={handleAnalyze}
                        disabled={!file || status === "uploading"}
                    >
                        {status === "uploading" ? (
                            <><Loader2 size={16} className="spin" /> 분석 중...</>
                        ) : (
                            <><Camera size={16} /> AI로 분석하기</>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
