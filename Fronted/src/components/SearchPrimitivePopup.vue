<template>
  <DxPopup
    v-model:visible="this.popupForSearchPrimitiveVisible"
    @showing="onShowing"
    :show-title="true"
    title="Поиск примитива"
    :width="900"
    :height="450"
    :hide-on-outside-click="false"
    :show-close-button="false"
    :drag-enabled="false"
    position="center"
    :enable-body-scroll="false"
    content-template="popup-content"
  >
    <template #popup-content>
      <DxValidationGroup name="CreateProject">
        <div class="container">
          <div class="row">
            <div class="col">
              <DxSelectBox
                v-model:value="this.editData.primitive"
                :items="['Диссонанс', 'Мотив', 'Сниппет', 'Цепочка', 'Матричный профиль']"
                :search-enabled="false"
                :wrap-item-text="true"
                label="Примитив"
                labelMode="static"
                :width="250"
                v-model:validation-status="this.validationStatus[0]"
              >
                <DxValidator> <DxRequiredRule message="Выберите примитив" /> </DxValidator>
              </DxSelectBox>
            </div>
            <div class="col">
              <DxNumberBox
                v-model:value="this.editData.subseqLen"
                label="Длина подпоследовательности"
                labelMode="static"
                :min="3"
                v-model:validation-status="this.validationStatus[1]"
              >
                <DxValidator>
                  <DxRequiredRule message="Введите длину подпоследовательности" />
                  <DxRangeRule
                    :max="this.minSubseqLen / 2"
                    :message="`Длина подпоследовательности должна быть не больше ${this.minSubseqLen / 2}`"
                    type="range"
                  />
                </DxValidator>
              </DxNumberBox>
            </div>
            <div class="col">
              <DxNumberBox
                v-model:value="this.editData.topK"
                label="top-k"
                labelMode="static"
                :min="1"
                v-model:validation-status="this.validationStatus[2]"
                v-if="this.editData.primitive != 'Матричный профиль' && this.editData.primitive"
              >
                <DxValidator>
                  <DxRequiredRule message="Введите top скольки примитивов хотите найти" />
                  <DxRangeRule
                    :max="this.minSubseqLen - this.editData.subseqLen + 2"
                    :message="
                      this.minSubseqLen >= this.editData.subseqLen
                        ? `Должно быть не больше top ${this.minSubseqLen - this.editData.subseqLen + 2} `
                        : 'Введите корректную длину подпоследовательности'
                    "
                    type="range"
                  />
                </DxValidator>
              </DxNumberBox>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <DxDataGrid
                id="dgSearchPrimitive"
                ref="dgSearchPrimitive"
                :column-hiding-enabled="false"
                :data-source="this.gridDataSource"
                :remote-operations="false"
                :row-Alternation-Enabled="true"
                :show-borders="true"
                :show-row-lines="true"
                :word-wrap-enabled="true"
                @key-down="KeyDown"
                v-model:selected-row-keys="this.selectedItemKeys"
                @selection-changed="onSelectionChangedDg"
                :height="230"
              >
                <DxColumn caption="Название координат" data-field="name" />
                <DxColumn caption="Длина" data-field="len" alignment="left" width="120" />
                <DxColumn caption="Описание" data-field="description" />

                <DxGroupPanel :visible="false" />
                <DxGrouping :auto-expand-all="false" />
                <DxFilterRow :visible="false" />
                <DxHeaderFilter :visible="false" />
                <DxScrolling mode="standard" />
                <DxSelection mode="multiple" />
              </DxDataGrid>

              <DxValidationSummary
                id="Summary"
                v-model:items="this.validationMessages"
              ></DxValidationSummary>
            </div>
          </div>
        </div>
        <div class="buttons">
          <DxButton
            hint="Найти"
            :disabled="!this.selectedItemKeys.length"
            type="success"
            stylingMode="outlined"
            @click="customSaveButtonClick"
            >Найти</DxButton
          >
          <DxButton
            hint="Отменить"
            type="danger"
            stylingMode="outlined"
            @click="customCancelButtonClick"
            >Отменить</DxButton
          >
        </div>
      </DxValidationGroup>
    </template>
  </DxPopup>
</template>

<script>
import { DxPopup } from 'devextreme-vue/popup'
import DxButton from 'devextreme-vue/button'
import { DxNumberBox } from 'devextreme-vue/number-box'
import DxValidationGroup from 'devextreme-vue/validation-group'
import { DxValidator, DxRequiredRule, DxRangeRule } from 'devextreme-vue/validator'
import { DxValidationSummary } from 'devextreme-vue/validation-summary'
import { DxSelectBox } from 'devextreme-vue/select-box'
import {
  DxDataGrid,
  DxColumn,
  DxFilterRow,
  DxHeaderFilter,
  DxGroupPanel,
  DxGrouping,
  DxScrolling,
  DxSelection
} from 'devextreme-vue/data-grid'
import axios from 'axios'

export default {
  name: 'SearchPrimitivePopup',
  components: {
    DxPopup,
    DxButton,
    DxNumberBox,
    DxValidationGroup,
    DxValidator,
    DxRequiredRule,
    DxRangeRule,
    DxValidationSummary,
    DxSelectBox,
    DxDataGrid,
    DxColumn,
    DxFilterRow,
    DxHeaderFilter,
    DxGroupPanel,
    DxGrouping,
    DxScrolling,
    DxSelection
  },
  props: {
    tsIds: Array
  },
  emits: ['childData'],
  data() {
    return {
      editData: { topK: null },
      validationStatus: ['valid', 'valid', 'valid'],
      popupForSearchPrimitiveVisible: false,
      gridDataSource: [],
      selectedItemKeys: [],
      minSubseqLen: Infinity,
      validationMessages: []
    }
  },
  methods: {
    start(popupVisible) {
      this.popupForSearchPrimitiveVisible = popupVisible
    },
    async onShowing() {
      this.validationStatus.fill('valid')
      this.validationMessages = []
      this.gridDataSource = await axios
        .get('/time-series/get-for-data-grid', {
          params: {
            ts_ids: this.tsIds
          },
          paramsSerializer: {
            indexes: null
          }
        })
        .then((res) => {
          return res.data
        })
        .catch((error) => {
          console.error(error)
        })
    },
    customSaveButtonClick(e) {
      var res = e.validationGroup.validate()
      if (res.isValid) {
        this.$emit('childData', this.editData, this.selectedItemKeys)
        this.customCancelButtonClick()
      }
    },
    customCancelButtonClick() {
      this.popupForSearchPrimitiveVisible = false
      this.editData = { topK: null }
      this.selectedItemKeys = []
    },
    onSelectionChangedDg() {
      if (this.selectedItemKeys.length)
        this.minSubseqLen = Math.min(...this.selectedItemKeys.map((x) => x.len)) - 1
      else this.minSubseqLen = Infinity
    },
    KeyDown(e) {
      if (e.event.key == 'Enter') {
        e.event.preventDefault()
      }
    }
  }
}
</script>

<style scoped>
.row {
  margin-bottom: 10px;
}
</style>
