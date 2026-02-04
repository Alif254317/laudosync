interface AuditResult {
  success: boolean
  audit_id: string | null
  classification: string
  summary: string
  concordant_findings: string[]
  discrepancies: Array<{
    type: string
    severity: string
    description: string
    official_says: string
    auditor_says: string
  }>
  has_critical_alert: boolean
  critical_alert_text: string | null
  technical_note: string | null
  report_url: string | null
  extracted_texts: {
    official: string
    auditor: string
  }
}

export const useAudit = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const loading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<AuditResult | null>(null)

  const analyzeReports = async (
    officialPdf: File,
    auditorPdf: File,
    patientName: string,
    examType: string,
    examDate: string
  ) => {
    loading.value = true
    error.value = null
    result.value = null

    const formData = new FormData()
    formData.append('official_pdf', officialPdf)
    formData.append('auditor_pdf', auditorPdf)
    formData.append('patient_name', patientName || 'Não informado')
    formData.append('exam_type', examType || 'Não informado')
    if (examDate) {
      formData.append('exam_date', examDate)
    }

    try {
      const response = await fetch(`${apiUrl}/api/audits`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erro ao processar auditoria')
      }

      result.value = await response.json()
    } catch (e: any) {
      error.value = e.message || 'Erro desconhecido'
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    loading.value = false
    error.value = null
    result.value = null
  }

  return {
    loading,
    error,
    result,
    analyzeReports,
    reset
  }
}
