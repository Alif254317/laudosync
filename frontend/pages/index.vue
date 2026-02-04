<template>
  <div class="min-h-screen py-8 px-4">
    <!-- Header -->
    <div class="max-w-4xl mx-auto mb-8">
      <div class="bg-white/95 backdrop-blur rounded-2xl shadow-xl p-6 text-center">
        <h1 class="text-3xl font-bold text-purple-800 mb-2">
          Elo System
        </h1>
        <h2 class="text-xl text-gray-600">LaudoSync - Auditoria Comparativa de Laudos</h2>
      </div>
    </div>

    <!-- Conteúdo Principal -->
    <div class="max-w-4xl mx-auto">
      <div class="bg-white/95 backdrop-blur rounded-2xl shadow-xl p-6">

        <!-- Formulário de Upload -->
        <div v-if="!result" class="space-y-6">
          <!-- Upload dos PDFs -->
          <div class="grid md:grid-cols-2 gap-6">
            <!-- Laudo Oficial -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Laudo Oficial (A)
              </label>
              <div
                class="border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer"
                :class="officialPdf ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'"
                @click="$refs.officialInput.click()"
                @dragover.prevent
                @drop.prevent="handleDrop($event, 'official')"
              >
                <input
                  ref="officialInput"
                  type="file"
                  accept=".pdf"
                  class="hidden"
                  @change="handleFileSelect($event, 'official')"
                />
                <div v-if="officialPdf" class="text-green-600">
                  <UIcon name="i-heroicons-document-check" class="w-10 h-10 mx-auto mb-2" />
                  <p class="font-medium truncate">{{ officialPdf.name }}</p>
                  <p class="text-sm text-gray-500">{{ formatFileSize(officialPdf.size) }}</p>
                </div>
                <div v-else class="text-gray-500">
                  <UIcon name="i-heroicons-document-plus" class="w-10 h-10 mx-auto mb-2" />
                  <p>Clique ou arraste o PDF</p>
                  <p class="text-sm">Laudo original do médico</p>
                </div>
              </div>
            </div>

            <!-- Laudo Auditor -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Laudo Auditor (B)
              </label>
              <div
                class="border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer"
                :class="auditorPdf ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'"
                @click="$refs.auditorInput.click()"
                @dragover.prevent
                @drop.prevent="handleDrop($event, 'auditor')"
              >
                <input
                  ref="auditorInput"
                  type="file"
                  accept=".pdf"
                  class="hidden"
                  @change="handleFileSelect($event, 'auditor')"
                />
                <div v-if="auditorPdf" class="text-green-600">
                  <UIcon name="i-heroicons-document-check" class="w-10 h-10 mx-auto mb-2" />
                  <p class="font-medium truncate">{{ auditorPdf.name }}</p>
                  <p class="text-sm text-gray-500">{{ formatFileSize(auditorPdf.size) }}</p>
                </div>
                <div v-else class="text-gray-500">
                  <UIcon name="i-heroicons-document-plus" class="w-10 h-10 mx-auto mb-2" />
                  <p>Clique ou arraste o PDF</p>
                  <p class="text-sm">Laudo do auditor (cego)</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Dados do Exame (Opcionais) -->
          <div class="border-t pt-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-4">Dados do Exame (opcional)</h3>
            <div class="grid md:grid-cols-3 gap-4">
              <UFormGroup label="Nome do Paciente">
                <UInput v-model="patientName" placeholder="Ex: João Silva" />
              </UFormGroup>
              <UFormGroup label="Tipo de Exame">
                <UInput v-model="examType" placeholder="Ex: TC Crânio" />
              </UFormGroup>
              <UFormGroup label="Data do Exame">
                <UInput v-model="examDate" type="date" />
              </UFormGroup>
            </div>
          </div>

          <!-- Botão de Análise -->
          <div class="flex justify-center pt-4">
            <UButton
              size="xl"
              color="primary"
              :disabled="!canAnalyze || loading"
              :loading="loading"
              @click="analyze"
            >
              <UIcon name="i-heroicons-sparkles" class="mr-2" />
              {{ loading ? 'Analisando...' : 'Analisar Laudos' }}
            </UButton>
          </div>

          <!-- Erro -->
          <UAlert
            v-if="error"
            color="red"
            variant="soft"
            :title="error"
            icon="i-heroicons-exclamation-circle"
          />
        </div>

        <!-- Resultado -->
        <div v-else class="space-y-6">
          <!-- Botão Voltar -->
          <div class="flex justify-between items-center">
            <UButton
              variant="ghost"
              color="gray"
              @click="resetForm"
            >
              <UIcon name="i-heroicons-arrow-left" class="mr-2" />
              Nova Análise
            </UButton>

            <UButton
              v-if="result.report_url"
              color="primary"
              @click="downloadReport"
            >
              <UIcon name="i-heroicons-arrow-down-tray" class="mr-2" />
              Baixar Relatório PDF
            </UButton>
          </div>

          <!-- Status Badge -->
          <div class="text-center">
            <div
              class="inline-block px-8 py-4 rounded-xl text-white font-bold text-xl"
              :class="getStatusClass(result.classification)"
            >
              {{ result.classification }}
            </div>
          </div>

          <!-- Alerta Crítico -->
          <UAlert
            v-if="result.has_critical_alert"
            color="red"
            variant="solid"
            icon="i-heroicons-exclamation-triangle"
          >
            <template #title>ALERTA CRÍTICO</template>
            <template #description>{{ result.critical_alert_text }}</template>
          </UAlert>

          <!-- Resumo -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="font-semibold text-gray-700 mb-2">Resumo da Análise</h3>
            <p class="text-gray-600">{{ result.summary }}</p>
          </div>

          <!-- Achados Concordantes -->
          <div v-if="result.concordant_findings?.length" class="bg-green-50 rounded-xl p-4">
            <h3 class="font-semibold text-green-700 mb-3">
              <UIcon name="i-heroicons-check-circle" class="inline mr-2" />
              Achados Concordantes
            </h3>
            <ul class="space-y-2">
              <li
                v-for="(finding, i) in result.concordant_findings"
                :key="i"
                class="flex items-start text-green-800"
              >
                <UIcon name="i-heroicons-check" class="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
                <span>{{ finding }}</span>
              </li>
            </ul>
          </div>

          <!-- Discrepâncias -->
          <div v-if="result.discrepancies?.length" class="space-y-4">
            <h3 class="font-semibold text-gray-700">
              <UIcon name="i-heroicons-exclamation-circle" class="inline mr-2" />
              Discrepâncias Identificadas
            </h3>

            <div
              v-for="(disc, i) in result.discrepancies"
              :key="i"
              class="border rounded-xl overflow-hidden"
              :class="getSeverityBorderClass(disc.severity)"
            >
              <div
                class="px-4 py-2 font-medium text-white flex justify-between items-center"
                :class="getSeverityBgClass(disc.severity)"
              >
                <span>Discrepância #{{ i + 1 }}</span>
                <span class="text-sm uppercase">{{ disc.severity }}</span>
              </div>
              <div class="p-4 space-y-2 bg-white">
                <p><strong>Tipo:</strong> {{ disc.type }}</p>
                <p><strong>Descrição:</strong> {{ disc.description }}</p>
                <div class="grid md:grid-cols-2 gap-4 mt-3">
                  <div class="bg-blue-50 rounded-lg p-3">
                    <p class="text-sm font-medium text-blue-700 mb-1">Laudo Oficial diz:</p>
                    <p class="text-blue-900">{{ disc.official_says }}</p>
                  </div>
                  <div class="bg-purple-50 rounded-lg p-3">
                    <p class="text-sm font-medium text-purple-700 mb-1">Laudo Auditor diz:</p>
                    <p class="text-purple-900">{{ disc.auditor_says }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Nota Técnica -->
          <div v-if="result.technical_note" class="bg-gray-100 rounded-xl p-4">
            <h3 class="font-semibold text-gray-700 mb-2">
              <UIcon name="i-heroicons-information-circle" class="inline mr-2" />
              Nota Técnica
            </h3>
            <p class="text-gray-600 italic">{{ result.technical_note }}</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-6 text-white/80 text-sm">
        <p>LaudoSync - Sistema de Auditoria Comparativa de Laudos</p>
        <p>Desenvolvido por Elo System</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { loading, error, result, analyzeReports, reset } = useAudit()

const officialPdf = ref<File | null>(null)
const auditorPdf = ref<File | null>(null)
const patientName = ref('')
const examType = ref('')
const examDate = ref('')

const canAnalyze = computed(() => officialPdf.value && auditorPdf.value)

const handleFileSelect = (event: Event, type: 'official' | 'auditor') => {
  const input = event.target as HTMLInputElement
  if (input.files?.length) {
    if (type === 'official') {
      officialPdf.value = input.files[0]
    } else {
      auditorPdf.value = input.files[0]
    }
  }
}

const handleDrop = (event: DragEvent, type: 'official' | 'auditor') => {
  const files = event.dataTransfer?.files
  if (files?.length && files[0].type === 'application/pdf') {
    if (type === 'official') {
      officialPdf.value = files[0]
    } else {
      auditorPdf.value = files[0]
    }
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const analyze = async () => {
  if (!officialPdf.value || !auditorPdf.value) return

  await analyzeReports(
    officialPdf.value,
    auditorPdf.value,
    patientName.value,
    examType.value,
    examDate.value
  )
}

const resetForm = () => {
  officialPdf.value = null
  auditorPdf.value = null
  patientName.value = ''
  examType.value = ''
  examDate.value = ''
  reset()
}

const downloadReport = () => {
  if (result.value?.report_url) {
    window.open(result.value.report_url, '_blank')
  }
}

const getStatusClass = (classification: string) => {
  const classes: Record<string, string> = {
    'CONCORDÂNCIA TOTAL': 'bg-green-500',
    'CONCORDÂNCIA PARCIAL': 'bg-yellow-500',
    'DISCORDÂNCIA': 'bg-red-500'
  }
  return classes[classification] || 'bg-gray-500'
}

const getSeverityBgClass = (severity: string) => {
  const classes: Record<string, string> = {
    'baixa': 'bg-gray-500',
    'média': 'bg-yellow-500',
    'alta': 'bg-orange-500',
    'crítica': 'bg-red-500'
  }
  return classes[severity] || 'bg-gray-500'
}

const getSeverityBorderClass = (severity: string) => {
  const classes: Record<string, string> = {
    'baixa': 'border-gray-300',
    'média': 'border-yellow-300',
    'alta': 'border-orange-300',
    'crítica': 'border-red-300'
  }
  return classes[severity] || 'border-gray-300'
}
</script>
