import React from 'react'
import { TextInput } from './TextInput'
import { SelectInput } from './SelectInput'

interface FormFieldProps {
  type: 'text' | 'email' | 'password' | 'select'
  name: string
  label: string
  value: string
  onChange: (value: string) => void
  error?: string
  options?: Array<{ value: string; label: string }>
  required?: boolean
}

export const FormField: React.FC<FormFieldProps> = (props) => {
  if (props.type === 'select') {
    return <SelectInput {...props} options={props.options || []} />
  }
  return <TextInput {...props} type={props.type} />
}

