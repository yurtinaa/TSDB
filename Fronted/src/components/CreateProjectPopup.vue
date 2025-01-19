<template>
  <DxValidationGroup name="CreateProject">
    <table>
      <tr>
        <td>
          <DxTextBox
            v-model:value="this.editRowValue.project_name"
            label="Название проекта"
            labelMode="static"
            v-model:validation-status="this.validationStatus"
            :maxLength="50"
          >
            <DxValidator>
              <DxRequiredRule message="Введите название проекта" />
            </DxValidator>
          </DxTextBox>
        </td>
      </tr>
      <tr>
        <td>
          <DxTextBox
            v-model:value="this.editRowValue.description"
            label="Описание"
            labelMode="static"
          >
          </DxTextBox>
        </td>
      </tr>
      <tr>
        <td>
          <div>
            <FileUploader
              id="fu2"
              ref="fileUploader"
              :options="{
                text: 'Загрузить временной ряд',
                url: 'http://127.0.0.1:8000/file/upload-file'
              }"
              :isDisabled="Boolean(this.tsIds.length)"
              :isNewProject="true"
              @fUData="acceptFUData"
              @disabledButtons="disabledButtons"
            />
            <DxTooltip
              :hide-on-outside-click="false"
              target="#fu2"
              show-event="mouseenter"
              hide-event="mouseleave"
            >
              <div class="hint">
                Можно загрузить один файл формата .txt! Как нужно заполнять файл: <br />
                1строка:Timestamp(если есть временные метки, иначе пусто),Название координат
                1(Описание),Название координат 2(Описание),...<br />
                2строка:Метка времени,Значение координаты 1, Значение координаты 2,...<br />
                Длина меток и координат должна быть одинаковой, разделителем служит ','.<br />
                Первый столбец временные метки, а каждый последующий координаты.<br />
                Если не будет описания координат, не ставьте ().
              </div>
            </DxTooltip>
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <DxButton
            :disabled="!this.tsIds.length"
            hint="Добавить примитив в очередь"
            @click="primitiveSearchButtonClick"
            >Найти примитив
          </DxButton>
        </td>
      </tr>
      <tr>
        <td>
          <DxDataGrid
            id="dgCreateProject"
            ref="dgCreateProject"
            :column-hiding-enabled="false"
            :data-source="this.gridDataSource"
            :remote-operations="false"
            :row-Alternation-Enabled="true"
            :show-borders="true"
            :show-row-lines="true"
            :word-wrap-enabled="true"
            @key-down="KeyDown"
            :height="300"
          >
            <DxColumn alignment="center" type="buttons" width="100">
              <gridButton name="delete" />
            </DxColumn>

            <DxColumn caption="Название примитива" data-field="name" />
            <DxColumn
              caption="Длина подпоследовательности"
              data-field="subseqLen"
              alignment="left"
              width="220"
            />

            <DxGroupPanel :visible="false" />
            <DxGrouping :auto-expand-all="false" />
            <DxFilterRow :visible="false" />
            <DxHeaderFilter :visible="false" />
            <DxScrolling mode="standard" />
            <DxEditing :allow-deleting="true" mode="row" />
          </DxDataGrid>
        </td>
      </tr>
    </table>
    <DxValidationSummary
      v-show="this.validationStatus != 'valid'"
      id="Summary"
    ></DxValidationSummary>
    <div class="buttons">
      <DxButton
        hint="Сохранить"
        type="success"
        stylingMode="outlined"
        @click="customSaveButtonClick"
        :disabled="this.isDisabledButtons"
        >Сохранить</DxButton
      >
      <DxButton
        hint="Отменить"
        type="danger"
        stylingMode="outlined"
        @click="customCancelButtonClick"
        :disabled="this.isDisabledButtons"
        >Отменить</DxButton
      >
    </div>
  </DxValidationGroup>
  <SearchPrimitivePopup :tsIds="this.tsIds" @childData="acceptData" ref="SearchPrimitivePopup" />
</template>

<script>
import {
  DxDataGrid,
  DxColumn,
  DxFilterRow,
  DxHeaderFilter,
  DxEditing,
  DxButton as gridButton,
  DxGroupPanel,
  DxGrouping,
  DxScrolling
} from 'devextreme-vue/data-grid'
import DxButton from 'devextreme-vue/button'
import { DxTextBox } from 'devextreme-vue/text-box'
import { DxValidator, DxRequiredRule } from 'devextreme-vue/validator'
import { DxValidationSummary } from 'devextreme-vue/validation-summary'
import notify from 'devextreme/ui/notify'
import DxValidationGroup from 'devextreme-vue/validation-group'
import SearchPrimitivePopup from './SearchPrimitivePopup.vue'
import axios from 'axios'
import FileUploader from './FileUploader.vue'
import { DxTooltip } from 'devextreme-vue/tooltip'

export default {
  name: 'CreateProjectPopup',
  components: {
    DxDataGrid,
    DxColumn,
    DxFilterRow,
    DxHeaderFilter,
    DxEditing,
    gridButton,
    DxGroupPanel,
    DxGrouping,
    DxScrolling,
    DxButton,
    DxTextBox,
    DxValidator,
    DxValidationSummary,
    DxRequiredRule,
    DxValidationGroup,
    SearchPrimitivePopup,
    FileUploader,
    DxTooltip
  },
  emits: ['popupCloseButtonClick'],
  data() {
    return {
      editRowValue: {},
      validationStatus: 'valid',
      tsIds: [],
      gridDataSource: [],
      isDisabledButtons: false
    }
  },
  methods: {
    onShowing() {
      this.validationStatus = 'valid'
    },
    customSaveButtonClick(e) {
      var res = e.validationGroup.validate()
      if (res.isValid) {
        axios
          .post('/project/insert', {
            project: this.editRowValue,
            primitives: this.gridDataSource,
            ts_ids: this.tsIds
          })
          .then((res) => {
            if (res == undefined || res.status != 200 || res.data != true)
              notify(
                { message: 'Ошибка при сохранении проекта', type: 'error', displayTime: 2000 },
                { position: 'center' }
              )
            else {
              this.tsIds = []
              this.customCancelButtonClick()
            }
          })
      }
    },
    customCancelButtonClick() {
      this.editRowValue = {}
      this.gridDataSource = []
      if (this.tsIds.length) {
        axios
          .delete('/time-series/delete', {
            params: { ts_ids: this.tsIds },
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
      }
      this.tsIds = []
      this.$refs['fileUploader'].clear()
      this.$emit('popupCloseButtonClick')
    },
    primitiveSearchButtonClick() {
      this.$refs['SearchPrimitivePopup'].start(true)
    },
    acceptData(editData, selectedItemKeys) {
      selectedItemKeys.forEach((el) => {
        let row = {
          ts_id: el.id,
          primitive_name: editData.primitive,
          name: `${editData.primitive}(${el.name})${editData.primitive == 'Матричный профиль' ? '' : `_top-${editData.topK}`}`,
          subseqLen: editData.subseqLen,
          topK: editData.topK
        }
        let findEl = this.gridDataSource.find(
          (i) =>
            i.ts_id == row.ts_id &&
            i.primitive_name == row.primitive_name &&
            i.subseqLen == row.subseqLen
        )
        if (findEl) {
          if (row.primitive_name == 'Матричный профиль') {
            return
          } else {
            if (row.topK > findEl.topK) {
              this.gridDataSource = this.gridDataSource.filter((el) => {
                return el != findEl
              })
            } else {
              return
            }
          }
        }
        this.gridDataSource.push(row)
      })
      this.gridDataSource = this.gridDataSource.sort((a, b) => a.name.localeCompare(b.name))
      this.$refs['dgCreateProject'].instance.refresh()
    },
    acceptFUData(tsIds) {
      this.tsIds = tsIds
    },
    disabledButtons(isDisabled) {
      this.isDisabledButtons = isDisabled
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
td {
  width: 100%;
}
</style>
