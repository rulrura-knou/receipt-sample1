import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getReceipt, updateReceipt, deleteReceipt, imageUrl } from '../api/receipts'
import type { ReceiptUpdate } from '../types/receipt'

const CATEGORIES = ['식비', '교통비', '쇼핑', '의료비', '여가', '기타']

export default function DetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<ReceiptUpdate>({})
  const [confirmDelete, setConfirmDelete] = useState(false)

  const { data: receipt, isLoading } = useQuery({
    queryKey: ['receipt', id],
    queryFn: () => getReceipt(id!),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (data: ReceiptUpdate) => updateReceipt(id!, data),
    onSuccess: updated => {
      queryClient.setQueryData(['receipt', id], updated)
      queryClient.invalidateQueries({ queryKey: ['receipts'] })
      setEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteReceipt(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['receipts'] })
      navigate('/')
    },
  })

  const startEdit = () => {
    setForm({
      store_name: receipt?.store_name ?? '',
      date: receipt?.date ?? '',
      total_amount: receipt?.total_amount ?? 0,
      category: receipt?.category ?? '기타',
      memo: receipt?.memo ?? '',
    })
    setEditing(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-gray-400">
        불러오는 중...
      </div>
    )
  }
  if (!receipt) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 text-gray-400">
        <p>영수증을 찾을 수 없습니다</p>
        <button onClick={() => navigate('/')} className="text-indigo-600 text-sm hover:underline">
          대시보드로
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-600 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-bold text-gray-900">영수증 상세</h1>
          </div>
          {!editing && (
            <div className="flex items-center gap-2">
              <button
                onClick={startEdit}
                className="text-sm px-3 py-1.5 text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 transition-colors"
              >
                수정
              </button>
              <button
                onClick={() => setConfirmDelete(true)}
                className="text-sm px-3 py-1.5 text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
              >
                삭제
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8 space-y-4">
        {/* 영수증 이미지 */}
        {receipt.image_filename && (
          <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            <img
              src={imageUrl(receipt.image_filename)}
              alt="영수증"
              className="w-full max-h-72 object-contain bg-gray-50"
            />
          </div>
        )}

        {/* 정보 카드 */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          {editing ? (
            <div className="space-y-4">
              <FormField label="상호명">
                <input
                  className="input"
                  value={form.store_name ?? ''}
                  onChange={e => setForm(f => ({ ...f, store_name: e.target.value }))}
                />
              </FormField>
              <FormField label="날짜">
                <input
                  type="date"
                  className="input"
                  value={form.date ?? ''}
                  onChange={e => setForm(f => ({ ...f, date: e.target.value }))}
                />
              </FormField>
              <FormField label="합계 금액 (원)">
                <input
                  type="number"
                  className="input"
                  value={form.total_amount ?? 0}
                  onChange={e => setForm(f => ({ ...f, total_amount: Number(e.target.value) }))}
                />
              </FormField>
              <FormField label="카테고리">
                <select
                  className="input"
                  value={form.category ?? '기타'}
                  onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                >
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </FormField>
              <FormField label="메모">
                <textarea
                  className="input resize-none"
                  rows={3}
                  value={form.memo ?? ''}
                  onChange={e => setForm(f => ({ ...f, memo: e.target.value }))}
                />
              </FormField>

              {updateMutation.error && (
                <p className="text-sm text-red-500">
                  {updateMutation.error instanceof Error ? updateMutation.error.message : '수정 실패'}
                </p>
              )}

              <div className="flex gap-3 pt-1">
                <button
                  onClick={() => updateMutation.mutate(form)}
                  disabled={updateMutation.isPending}
                  className="flex-1 bg-indigo-600 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {updateMutation.isPending ? '저장 중...' : '저장'}
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  취소
                </button>
              </div>
            </div>
          ) : (
            <dl className="divide-y divide-gray-50">
              <InfoRow label="상호명" value={receipt.store_name || '-'} />
              <InfoRow label="날짜" value={receipt.date || '-'} />
              <InfoRow label="합계" value={`${receipt.total_amount.toLocaleString()}원`} highlight />
              <InfoRow label="카테고리" value={receipt.category} />
              <InfoRow label="메모" value={receipt.memo || '-'} />
            </dl>
          )}
        </div>

        {/* 품목 목록 */}
        {receipt.items.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-700 mb-4">구매 품목</h2>
            <div className="space-y-2">
              {receipt.items.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{item.name} × {item.quantity}</span>
                  <span className="font-medium text-gray-800">
                    {(item.price * item.quantity).toLocaleString()}원
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OCR 원본 텍스트 */}
        {receipt.raw_ocr && (
          <details className="bg-white rounded-2xl border border-gray-100 p-6 group">
            <summary className="text-sm font-medium text-gray-400 cursor-pointer select-none group-open:text-gray-600">
              OCR 원본 텍스트 보기
            </summary>
            <pre className="mt-4 text-xs text-gray-500 whitespace-pre-wrap leading-relaxed">
              {receipt.raw_ocr}
            </pre>
          </details>
        )}

        <p className="text-xs text-gray-400 text-center pb-4">
          등록: {new Date(receipt.created_at).toLocaleString('ko-KR')}
        </p>
      </main>

      {/* 삭제 확인 다이얼로그 */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-6">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
            <h3 className="font-bold text-gray-900 mb-2">영수증 삭제</h3>
            <p className="text-sm text-gray-500 mb-6">
              이 영수증을 삭제하면 복구할 수 없습니다. 계속하시겠습니까?
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => { setConfirmDelete(false); deleteMutation.mutate() }}
                disabled={deleteMutation.isPending}
                className="flex-1 bg-red-500 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-red-600 disabled:opacity-50 transition-colors"
              >
                {deleteMutation.isPending ? '삭제 중...' : '삭제'}
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                className="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
      {children}
    </div>
  )
}

function InfoRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex items-center justify-between py-3">
      <dt className="text-sm text-gray-500">{label}</dt>
      <dd className={highlight ? 'text-xl font-bold text-indigo-600' : 'text-sm font-medium text-gray-800'}>
        {value}
      </dd>
    </div>
  )
}
