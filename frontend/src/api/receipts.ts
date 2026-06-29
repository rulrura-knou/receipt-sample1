import type { Receipt, ReceiptUpdate } from '../types/receipt'

const BASE = '/api/receipts'

export async function listReceipts(): Promise<Receipt[]> {
  const res = await fetch(BASE)
  if (!res.ok) throw new Error('목록 조회 실패')
  return res.json()
}

export async function getReceipt(id: string): Promise<Receipt> {
  const res = await fetch(`${BASE}/${id}`)
  if (!res.ok) throw new Error('영수증을 찾을 수 없습니다')
  return res.json()
}

export async function uploadReceipt(file: File): Promise<Receipt> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('업로드 실패')
  return res.json()
}

export async function updateReceipt(id: string, data: ReceiptUpdate): Promise<Receipt> {
  const res = await fetch(`${BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('수정 실패')
  return res.json()
}

export async function deleteReceipt(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('삭제 실패')
}

export function imageUrl(filename: string): string {
  return `/static/images/${filename}`
}
