import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadReceipt, imageUrl } from '../api/receipts'
import UploadZone from '../components/UploadZone'

export default function UploadPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [preview, setPreview] = useState<string | null>(null)

  const { mutate, data, isPending, isSuccess, error, reset } = useMutation({
    mutationFn: uploadReceipt,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['receipts'] })
    },
  })

  const handleFile = (file: File) => {
    setPreview(URL.createObjectURL(file))
    reset()
    mutate(file)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <button onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-xl font-bold text-gray-900">영수증 추가</h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">
        {!isSuccess ? (
          <div className="space-y-6">
            <UploadZone onFile={handleFile} disabled={isPending} />

            {preview && (
              <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                <img
                  src={preview}
                  alt="선택된 영수증"
                  className="w-full max-h-64 object-contain"
                />
              </div>
            )}

            {isPending && (
              <div className="flex items-center justify-center gap-3 py-6 text-indigo-600">
                <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-medium">OCR 분석 중...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 text-red-600 rounded-xl p-4 text-sm">
                업로드 실패: {error instanceof Error ? error.message : '알 수 없는 오류'}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-gray-100 p-6 space-y-6">
            <div className="flex items-center gap-2 text-green-600">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span className="font-semibold">OCR 분석 완료!</span>
            </div>

            {data?.image_filename && (
              <div className="rounded-xl overflow-hidden border border-gray-100">
                <img
                  src={imageUrl(data.image_filename)}
                  alt="업로드된 영수증"
                  className="w-full max-h-52 object-contain bg-gray-50"
                />
              </div>
            )}

            <dl className="divide-y divide-gray-50">
              <InfoRow label="상호명" value={data?.store_name || '(인식 안 됨)'} />
              <InfoRow label="날짜" value={data?.date || '(인식 안 됨)'} />
              <InfoRow label="합계 금액" value={`${(data?.total_amount ?? 0).toLocaleString()}원`} highlight />
              <InfoRow label="카테고리" value={data?.category || '기타'} />
            </dl>

            <div className="flex gap-3 pt-2">
              <button
                onClick={() => navigate(`/receipts/${data?.id}`)}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors text-sm"
              >
                상세보기 / 수정
              </button>
              <button
                onClick={() => { setPreview(null); reset() }}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl font-medium hover:bg-gray-200 transition-colors text-sm"
              >
                추가 업로드
              </button>
            </div>
            <button
              onClick={() => navigate('/')}
              className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              대시보드로 돌아가기
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

function InfoRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex items-center justify-between py-3">
      <dt className="text-sm text-gray-500">{label}</dt>
      <dd className={highlight ? 'text-lg font-bold text-indigo-600' : 'text-sm font-medium text-gray-800'}>
        {value}
      </dd>
    </div>
  )
}
