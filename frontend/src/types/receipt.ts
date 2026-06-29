export interface ReceiptItem {
  name: string
  price: number
  quantity: number
}

export interface Receipt {
  id: string
  store_name: string
  date: string
  total_amount: number
  items: ReceiptItem[]
  category: string
  memo: string
  image_filename: string
  raw_ocr: string
  created_at: string
  updated_at: string
}

export interface ReceiptUpdate {
  store_name?: string
  date?: string
  total_amount?: number
  items?: ReceiptItem[]
  category?: string
  memo?: string
}
