import { useCallback, useState } from 'react'

interface Props {
  onFile: (file: File) => void
  disabled?: boolean
}

export default function UploadZone({ onFile, disabled }: Props) {
  const [dragging, setDragging] = useState(false)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) onFile(file)
    },
    [onFile],
  )

  return (
    <label
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={[
        'flex flex-col items-center justify-center gap-4 w-full h-64 rounded-2xl border-2 border-dashed cursor-pointer transition-colors',
        dragging ? 'border-indigo-400 bg-indigo-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100',
        disabled ? 'opacity-50 pointer-events-none' : '',
      ].join(' ')}
    >
      <svg className="w-14 h-14 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">영수증 사진을 드래그하거나 클릭하여 선택</p>
        <p className="text-xs text-gray-400 mt-1">JPG · PNG · WEBP 지원</p>
      </div>
      <input
        type="file"
        accept="image/*"
        className="hidden"
        disabled={disabled}
        onChange={e => e.target.files?.[0] && onFile(e.target.files[0])}
      />
    </label>
  )
}
