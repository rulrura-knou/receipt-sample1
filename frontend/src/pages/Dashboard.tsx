import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listReceipts } from '../api/receipts'
import FilterPanel, { type FilterValues } from '../components/FilterPanel'
import ReceiptCard from '../components/ReceiptCard'

const CATEGORY_STYLE: Record<string, { badge: string; bar: string }> = {
  '식비':  { badge: 'bg-orange-100 text-orange-700', bar: 'bg-orange-400' },
  '교통비': { badge: 'bg-blue-100 text-blue-700',   bar: 'bg-blue-400' },
  '쇼핑':  { badge: 'bg-purple-100 text-purple-700', bar: 'bg-purple-400' },
  '의료비': { badge: 'bg-red-100 text-red-700',      bar: 'bg-red-400' },
  '여가':  { badge: 'bg-green-100 text-green-700',  bar: 'bg-green-400' },
  '기타':  { badge: 'bg-gray-100 text-gray-600',    bar: 'bg-gray-400' },
}
const defaultStyle = { badge: 'bg-gray-100 text-gray-600', bar: 'bg-gray-400' }

/** OCR에서 추출한 날짜를 YYYY-MM-DD로 정규화 */
function normalizeDate(dateStr: string): string {
  if (!dateStr) return ''
  const parts = dateStr.replace(/[./]/g, '-').split('-')
  if (parts.length !== 3) return dateStr
  if (parts[0].length === 2) parts[0] = `20${parts[0]}`
  return `${parts[0]}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`
}

const EMPTY_FILTER: FilterValues = { startDate: '', endDate: '', minAmount: '', maxAmount: '' }

function isFilterActive(f: FilterValues) {
  return f.startDate || f.endDate || f.minAmount || f.maxAmount
}

export default function Dashboard() {
  const { data: receipts = [], isLoading } = useQuery({
    queryKey: ['receipts'],
    queryFn: listReceipts,
  })

  const [appliedFilter, setAppliedFilter] = useState<FilterValues>(EMPTY_FILTER)

  const filteredReceipts = receipts.filter(r => {
    const date = normalizeDate(r.date)
    if (appliedFilter.startDate && date && date < appliedFilter.startDate) return false
    if (appliedFilter.endDate && date && date > appliedFilter.endDate) return false
    if (appliedFilter.minAmount && r.total_amount < Number(appliedFilter.minAmount)) return false
    if (appliedFilter.maxAmount && r.total_amount > Number(appliedFilter.maxAmount)) return false
    return true
  })

  const filterActive = isFilterActive(appliedFilter)
  const totalAmount = filteredReceipts.reduce((sum, r) => sum + r.total_amount, 0)
  const avgAmount = filteredReceipts.length ? Math.round(totalAmount / filteredReceipts.length) : 0

  const byCategory = filteredReceipts.reduce<Record<string, number>>((acc, r) => {
    acc[r.category] = (acc[r.category] ?? 0) + r.total_amount
    return acc
  }, {})
  const sortedCategories = Object.entries(byCategory).sort((a, b) => b[1] - a[1])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">영수증 지출관리</h1>
          <Link
            to="/upload"
            className="bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            + 영수증 추가
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* 필터 */}
        <FilterPanel
          onSearch={setAppliedFilter}
          onReset={() => setAppliedFilter(EMPTY_FILTER)}
        />

        {/* 요약 통계 */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard label="총 지출" value={`${totalAmount.toLocaleString()}원`} gradient="from-indigo-500 to-indigo-600" />
          <StatCard label="영수증 수" value={`${filteredReceipts.length}건`} gradient="from-violet-500 to-violet-600" />
          <StatCard label="건당 평균" value={filteredReceipts.length ? `${avgAmount.toLocaleString()}원` : '-'} gradient="from-sky-500 to-sky-600" />
        </div>

        {/* 카테고리별 지출 */}
        {sortedCategories.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-700 mb-5">카테고리별 지출</h2>
            <div className="space-y-3">
              {sortedCategories.map(([cat, amt]) => {
                const style = CATEGORY_STYLE[cat] ?? defaultStyle
                return (
                  <div key={cat} className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 w-16 text-center ${style.badge}`}>
                      {cat}
                    </span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
                      <div
                        className={`${style.bar} h-2.5 rounded-full transition-all`}
                        style={{ width: `${totalAmount ? Math.round((amt / totalAmount) * 100) : 0}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-800 w-24 text-right shrink-0">
                      {amt.toLocaleString()}원
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* 영수증 목록 */}
        {isLoading ? (
          <div className="text-center py-20 text-gray-400">불러오는 중...</div>
        ) : receipts.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-400 mb-3">아직 영수증이 없습니다</p>
            <Link to="/upload" className="text-indigo-600 font-medium text-sm hover:underline">
              첫 영수증을 추가해보세요 →
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-gray-700">
                전체 영수증 ({filteredReceipts.length}
                {filterActive && <span className="text-gray-400 font-normal"> / {receipts.length}</span>}
                )
              </h2>
              {filterActive && (
                <span className="text-xs text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full font-medium">
                  필터 적용 중
                </span>
              )}
            </div>
            {filteredReceipts.length === 0 ? (
              <div className="text-center py-16 text-gray-400">
                조건에 맞는 영수증이 없습니다
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredReceipts.map(r => <ReceiptCard key={r.id} receipt={r} />)}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

function StatCard({ label, value, gradient }: { label: string; value: string; gradient: string }) {
  return (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-5 text-white`}>
      <p className="text-sm opacity-80 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}
