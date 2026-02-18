import { useState } from "react";
import { CheckCircle, Edit2, Plus, Trash2, AlertTriangle } from "lucide-react";

/**
 * OCRReviewForm - Shows extracted data for user review/edit before saving.
 * Props:
 *   mode: "assets" | "trades"
 *   data: extracted OCR data object
 *   onConfirm: (items) => void
 *   onCancel: () => void
 */
export default function OCRReviewForm({ mode, data, onConfirm, onCancel }) {
    const isAssets = mode === "assets";
    const rawItems = isAssets ? (data?.assets || []) : (data?.trades || []);

    const [items, setItems] = useState(rawItems.map((item, i) => ({ ...item, _id: i })));
    const [saving, setSaving] = useState(false);

    const updateItem = (id, field, value) => {
        setItems(prev => prev.map(item =>
            item._id === id ? { ...item, [field]: value } : item
        ));
    };

    const removeItem = (id) => {
        setItems(prev => prev.filter(item => item._id !== id));
    };

    const handleConfirm = async () => {
        setSaving(true);
        try {
            await onConfirm(items);
        } finally {
            setSaving(false);
        }
    };

    if (items.length === 0) {
        return (
            <div className="ocr-review-empty">
                <AlertTriangle size={32} />
                <p>인식된 데이터가 없습니다.</p>
                <p className="hint">다른 스크린샷을 시도해보세요.</p>
                <button className="ocr-cancel-btn" onClick={onCancel}>돌아가기</button>
            </div>
        );
    }

    return (
        <div className="ocr-review">
            <div className="ocr-review-header">
                <div className="ocr-review-title">
                    <Edit2 size={18} />
                    <span>인식 결과 확인 ({items.length}건)</span>
                </div>
                {data?.confidence && (
                    <span className={`ocr-confidence confidence-${data.confidence}`}>
                        신뢰도: {data.confidence === "high" ? "높음" : data.confidence === "medium" ? "보통" : "낮음"}
                    </span>
                )}
            </div>

            {data?.notes && (
                <div className="ocr-notes">
                    <AlertTriangle size={14} /> {data.notes}
                </div>
            )}

            <div className="ocr-items-list">
                {isAssets ? (
                    items.map(item => (
                        <AssetRow key={item._id} item={item} onChange={updateItem} onRemove={removeItem} />
                    ))
                ) : (
                    items.map(item => (
                        <TradeRow key={item._id} item={item} onChange={updateItem} onRemove={removeItem} />
                    ))
                )}
            </div>

            <div className="ocr-review-actions">
                <button className="ocr-cancel-btn" onClick={onCancel}>취소</button>
                <button className="ocr-confirm-btn" onClick={handleConfirm} disabled={saving}>
                    <CheckCircle size={16} />
                    {saving ? "저장 중..." : `${items.length}건 저장`}
                </button>
            </div>
        </div>
    );
}

function Field({ label, value, onChange, type = "text", options }) {
    return (
        <div className="ocr-field">
            <label className="ocr-field-label">{label}</label>
            {options ? (
                <select className="ocr-field-input" value={value || ""} onChange={e => onChange(e.target.value)}>
                    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
            ) : (
                <input
                    className="ocr-field-input"
                    type={type}
                    value={value ?? ""}
                    onChange={e => onChange(type === "number" ? parseFloat(e.target.value) || 0 : e.target.value)}
                />
            )}
        </div>
    );
}

function AssetRow({ item, onChange, onRemove }) {
    const update = (field, val) => onChange(item._id, field, val);
    return (
        <div className="ocr-item-card">
            <button className="ocr-item-remove" onClick={() => onRemove(item._id)}><Trash2 size={14} /></button>
            <div className="ocr-item-grid">
                <Field label="종목명" value={item.name} onChange={v => update("name", v)} />
                <Field label="종목코드" value={item.symbol} onChange={v => update("symbol", v)} />
                <Field label="자산유형" value={item.asset_type} onChange={v => update("asset_type", v)}
                    options={[
                        { value: "stock", label: "주식" },
                        { value: "etf", label: "ETF" },
                        { value: "fund", label: "펀드" },
                        { value: "crypto", label: "암호화폐" },
                        { value: "bond", label: "채권" },
                        { value: "cash", label: "현금" },
                    ]}
                />
                <Field label="통화" value={item.currency} onChange={v => update("currency", v)}
                    options={[
                        { value: "KRW", label: "KRW (원)" },
                        { value: "USD", label: "USD (달러)" },
                        { value: "JPY", label: "JPY (엔)" },
                    ]}
                />
                <Field label="수량" value={item.quantity} onChange={v => update("quantity", v)} type="number" />
                <Field label="평균매입가" value={item.buy_price} onChange={v => update("buy_price", v)} type="number" />
                <Field label="현재가" value={item.current_price} onChange={v => update("current_price", v)} type="number" />
                <Field label="증권사" value={item.brokerage} onChange={v => update("brokerage", v)} />
            </div>
        </div>
    );
}

function TradeRow({ item, onChange, onRemove }) {
    const update = (field, val) => onChange(item._id, field, val);
    return (
        <div className="ocr-item-card">
            <button className="ocr-item-remove" onClick={() => onRemove(item._id)}><Trash2 size={14} /></button>
            <div className="ocr-item-grid">
                <Field label="거래일" value={item.trade_date} onChange={v => update("trade_date", v)} type="date" />
                <Field label="종목명" value={item.name} onChange={v => update("name", v)} />
                <Field label="종목코드" value={item.symbol} onChange={v => update("symbol", v)} />
                <Field label="매수/매도" value={item.trade_type} onChange={v => update("trade_type", v)}
                    options={[
                        { value: "buy", label: "매수" },
                        { value: "sell", label: "매도" },
                    ]}
                />
                <Field label="수량" value={item.quantity} onChange={v => update("quantity", v)} type="number" />
                <Field label="단가" value={item.price} onChange={v => update("price", v)} type="number" />
                <Field label="거래금액" value={item.total_amount} onChange={v => update("total_amount", v)} type="number" />
                <Field label="수수료" value={item.fee} onChange={v => update("fee", v)} type="number" />
            </div>
        </div>
    );
}
