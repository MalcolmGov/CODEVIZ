import React from 'react'
import { Button } from '@/components/common/Button'

interface FormSubmitProps {
  onSubmit: (e: React.FormEvent) => void
  loading?: boolean
  children: React.ReactNode
}

export const FormSubmit: React.FC<FormSubmitProps> = ({ onSubmit, loading, children }) => (
  <form onSubmit={onSubmit} className="space-y-4">
    {children}
    <Button type="submit" loading={loading} size="lg" className="w-full">
      Submit
    </Button>
  </form>
)
