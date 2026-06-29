import { Link } from 'react-router-dom'
import type { Receipt } from '../types/receipt'
import { imageUrl } from '../api/receipts'

const CATEGORY_COLORS: Record<string, string> = {
  '식비': 'bg-orange-100 text-orange-700',
  '교통비': 'bg-blue-100 text-blue-700',
  '쇼핑': 'bg-purple-100 text-purple-700',
  '의료비': 'bg-red-100 text-red-700',
  '여가': 'bg-green-100 text-green-700',
  '기타': 'bg-gray-100 text-gray-600',
}

export default function ReceiptCard({ receipt }: { receipt: Receipt }) {
  const badgeClass = CATEGORY_COLORS[receipt.category] ?? 'bg-gray-100 text-gray-600'

  return (
    <Link
      to={`/receipts/${receipt.id}`}
      className="block bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow overflow-hidden"
    >
      {receipt.image_filename ? (
        <img
          src={imageUrl(receipt.image_filename)}
          alt="영수증"
          className="w-full h-40 object-cover"
        />
      ) : (
        <div className="w-full h-40 bg-gray-50 flex items-center justify-center">
          <svg className="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      )}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-1">
          <p className="font-semibold text-gray-900 truncate">
            {receipt.store_name || '상호명 없음'}
          </p>
          <span className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${badgeClass}`}>
            {receipt.category}
          </span>
        </div>
        <p className="text-xs text-gray-400 mb-3">{receipt.date || '날짜 없음'}</p>
        <p className="text-lg font-bold text-indigo-600">
          {receipt.total_amount.toLocaleString()}원
        </p>
      </div>
    </Link>
  )
}
