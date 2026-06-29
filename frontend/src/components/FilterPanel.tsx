import { useState } from 'react'

export interface FilterValues {
  startDate: string
  endDate: string
  minAmount: string
  maxAmount: string
}

interface FilterPanelProps {
  onSearch?: (values: FilterValues) => void
  onReset?: () => void
}

const EMPTY: FilterValues = { startDate: '', endDate: '', minAmount: '', maxAmount: '' }

export default function FilterPanel({ onSearch, onReset }: FilterPanelProps) {
  const [values, setValues] = useState<FilterValues>(EMPTY)

  const set = (key: keyof FilterValues) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setValues(prev => ({ ...prev, [key]: e.target.value }))

  const handleReset = () => {
    setValues(EMPTY)
    onReset?.()
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h2 className="font-semibold text-gray-700 mb-4">필터</h2>

      <div className="flex flex-col sm:flex-row gap-4">
        {/* 기간 */}
        <div className="flex-1">
          <p className="text-xs text-gray-500 mb-1.5">기간</p>
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={values.startDate}
              onChange={set('startDate')}
              className="flex-1 min-w-0 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <span className="text-gray-400 text-sm shrink-0">~</span>
            <input
              type="date"
              value={values.endDate}
              onChange={set('endDate')}
              min={values.startDate || undefined}
              className="flex-1 min-w-0 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
        </div>

        {/* 금액 */}
        <div className="flex-1">
          <p className="text-xs text-gray-500 mb-1.5">금액 (원)</p>
          <div className="flex items-center gap-2">
            <input
              type="number"
              placeholder="최소"
              min={0}
              value={values.minAmount}
              onChange={set('minAmount')}
              className="flex-1 min-w-0 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <span className="text-gray-400 text-sm shrink-0">~</span>
            <input
              type="number"
              placeholder="최대"
              min={0}
              value={values.maxAmount}
              onChange={set('maxAmount')}
              className="flex-1 min-w-0 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
        </div>

        {/* 버튼 */}
        <div className="flex items-end gap-2 shrink-0">
          <button
            onClick={handleReset}
            className="px-4 py-2 rounded-xl text-sm font-medium text-gray-500 border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            초기화
          </button>
          <button
            onClick={() => onSearch?.(values)}
            className="px-5 py-2 rounded-xl text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            검색
          </button>
        </div>
      </div>
    </div>
  )
}
