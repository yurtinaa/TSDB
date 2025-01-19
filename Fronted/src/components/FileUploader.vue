<template>
  <div>
    <DxFileUploader
      :select-button-text="this.options.text"
      label-text=""
      accept=".txt"
      :allowed-file-extensions="['.txt']"
      upload-mode="instantly"
      :upload-url="this.options.url"
      name="file"
      :min-file-size="1"
      @uploaded="onUploadEnd"
      @uploadError="onUploadError"
      @uploadStarted="onUploadStarted"
      v-show="!this.isDisabled && !this.isLoadData"
      ref="fileUploader"
    />
    <h3 style="margin: 20px" v-show="this.isLoadData">Идет загрузка {{ fileName }}</h3>
  </div>
</template>

<script>
import DxFileUploader from 'devextreme-vue/file-uploader'
import notify from 'devextreme/ui/notify'

export default {
  name: 'FileUploader',
  components: {
    DxFileUploader
  },
  props: {
    options: Object,
    isDisabled: Boolean,
    isNewProject: Boolean
  },
  emits: ['fUData', 'disabledButtons'],
  data() {
    return {
      isLoadData: false,
      fileName: ''
    }
  },
  methods: {
    onUploadEnd(e) {
      this.$emit('fUData', JSON.parse(e.request.response))
      this.$emit('disabledButtons', false)
      this.isLoadData = false
    },
    onUploadError(e) {
      if (!e.error.response) {
        notify(
          { message: 'Произошла ошибка при загрузке', type: 'error', displayTime: 3000 },
          { position: 'center' }
        )
      } else {
        notify(
          { message: JSON.parse(e.error.response).detail, type: 'error', displayTime: 3000 },
          { position: 'center' }
        )
      }
      this.$emit('disabledButtons', false)
      this.isLoadData = false
    },
    clear() {
      this.$refs['fileUploader'].instance.clear()
    },
    onUploadStarted(e) {
      this.$emit('disabledButtons', true)
      this.fileName = e.file.name
      this.isLoadData = true
    }
  }
}
</script>

<style scoped></style>
